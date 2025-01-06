#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <stdbool.h>
#include <unistd.h>

bool is_link(int argc, char const *argv[])
{
	for (int i = 0; i < argc; ++i)
	{
		if (strcmp(argv[i], "-c") == 0 || strcmp(argv[i], "-E") == 0 ||
				strcmp(argv[i], "-S") == 0)
			return false;
	}
	return true;
}

int main(int argc, char const *argv[])
{
	char const** new_argv = (char const**)malloc((argc + 100) * sizeof(char*));
	size_t idx = 0;
	if (strstr(argv[0], "++") != NULL)
		new_argv[idx++] = "/llvm-16/bin/clang++";
	else
		new_argv[idx++] = "/llvm-16/bin/clang";
	new_argv[idx++] = "-g";
	new_argv[idx++] = "-O0";
	new_argv[idx++] = "-Wno-error";
	new_argv[idx++] = "-flto";
	new_argv[idx++] = "-fno-omit-frame-pointer";
	new_argv[idx++] = "-DFUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION";

	// Important, otherwise mysterious errors might occur
	new_argv[idx++] = "-Qunused-arguments";

	for (int i = 1; i < argc; ++i)
	{
		if (strcmp(argv[i], "-s") == 0)
			continue;
		if (strstr(argv[i], "-O") == argv[i])
			continue;
		if (strstr(argv[i], "-g") == argv[i])
			continue;
		if (strstr(argv[i], "-flto") == argv[i])
			continue;
		if (strstr(argv[i], "-Werror") == argv[i])
			continue;
		if (strstr(argv[i], "-stdlib") == argv[i])
			continue;
		new_argv[idx++] = argv[i];
	}

	if (is_link(argc, argv))
	{
		new_argv[idx++] = "--ld-path=/llvm-16/bin/ld.lld";
		new_argv[idx++] = "-Wl,-plugin-opt=save-temps";
	}

	new_argv[idx] = NULL;

	if (getenv("SHOW_COMPILER_ARGS"))
	{
		for (int i = 0; i < argc; ++i)
			fprintf(stderr, "%s ", argv[i]);
		fprintf(stderr, "\n");
		for (char const** i = new_argv; *i; ++i)
			fprintf(stderr, "%s ", *i);
		fprintf(stderr, "\n");
	}

	execvp(new_argv[0], (char**)new_argv);
	abort();
	return 0;
}