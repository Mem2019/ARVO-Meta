import argparse
import os
import json
import subprocess
import io
from typing import List

def find_double_free(arvo_dir: str) -> List[str]:
	bugs = []
	for bug in os.scandir(os.path.join(arvo_dir, "meta")):
		if bug.is_file() and bug.name.endswith(".json"):
			assert bug.name[:-5].isdigit()
			with open(bug.path, 'r') as fd:
				if json.load(fd)["crash_type"] == "Heap-double-free":
					bugs.append((bug.path, int(bug.name[:-5])))
	return bugs

def build_bug_docker(bug_id: int,
	arvo_path: str, out_dir: str, log_fd: io.TextIOWrapper) -> bool:

	scripts_path = os.path.join(arvo_path, "scripts")
	out_path = os.path.join(out_dir, str(bug_id))
	subprocess.run(["mkdir", out_path], check=True)

	docker_name = "dfbench/%d" % bug_id

	log_fd.write((">>>>>>>>>>>>>> %d <<<<<<<<<<<<<<\n" % bug_id).encode())
	r = subprocess.run(["docker", "build",
		"--build-arg", "BUG_ID=%d" % bug_id, "-t", docker_name, "."],
		cwd=scripts_path, capture_output=True)
	log_fd.write(b">>> build stdout:\n")
	log_fd.write(r.stdout)
	log_fd.write(b">>> build stderr:\n")
	log_fd.write(r.stderr)
	if r.returncode != 0:
		subprocess.run(["docker", "image", "rm", "-f",
			docker_name, "n132/arvo:%d-vul" % bug_id], check=True)
		subprocess.run(["docker", "system", "prune", "--volumes", "--force"],
			check=True)
		return False
	r = subprocess.run(["docker", "run",
		"-v", "%s:/scripts" % scripts_path, "-v", "%s:/out" % out_path,
		"-it", docker_name, "bash", "-c", "arvo compile"],
		cwd=scripts_path, capture_output=True)
	log_fd.write(b">>> run stdout:\n")
	log_fd.write(r.stdout)
	log_fd.write(b">>> run stderr:\n")
	log_fd.write(r.stderr)
	log_fd.write(b'\n\n')
	subprocess.run(["docker", "image", "rm", "-f",
		docker_name, "n132/arvo:%d-vul" % bug_id], check=True)
	subprocess.run(["docker", "system", "prune", "--volumes", "--force"],
		check=True)
	return r.returncode == 0

def main():
	args = argparse.ArgumentParser()
	args.add_argument("arvo", type=str, help="Directory to ARVO-Meta")
	args.add_argument("out", type=str, help="Output directory")
	args.add_argument("--log", type=str, default="log.txt",
		help="File to store stdout and stderr")
	args = args.parse_args()
	args_arvo = os.path.abspath(args.arvo)
	args_out = os.path.abspath(args.out)
	subprocess.run(["rm", "-rf", args_out], check=True)
	subprocess.run(["mkdir", args_out], check=True)

	# TODO: DEL DEBUG
	# build_bug_docker(45687, args_arvo)

	success, total = 0, 0
	with open(args.log, "wb") as fd:
		for bug_path, bug_id in find_double_free(args_arvo):
			if build_bug_docker(bug_id, args_arvo, args_out, fd):
				success += 1
			total += 1
	print("%d/%d" % (success, total))
	return 0

if __name__ == "__main__":
	exit(main())