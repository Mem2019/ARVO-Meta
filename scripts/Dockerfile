ARG BUG_ID
FROM n132/arvo:${BUG_ID}-vul

COPY llvm.sh /llvm.sh
RUN bash /llvm.sh

ENV CC="/scripts/clang"
ENV CXX="/scripts/clang++"
RUN bash -c "sed -i 's/export SANITIZER=address/export SANITIZER=none/' `which arvo`" && \
	bash -c "sed -i -E 's/export FUZZING_ENGINE=[a-z]+/export FUZZING_ENGINE=libfuzzer/' `which arvo`"
