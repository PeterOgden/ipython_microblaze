COMPILER=
ARCHIVER=
CP=cp
COMPILER_FLAGS =
LIB=libmbio.a

EXTRA_ARCHIVE_FLAGS=rc

RELEASEDIR=../../../lib
INCLUDEDIR=../../../include
INCLUDES=-I./. -I${INCLUDEDIR}

MBIO_DIR = .
OUTS = *.o

MBIO_SRCS := $(wildcard *.c)
MBIO_OBJS = $(addprefix $(MBIO_DIR)/, $(MBIO_SRCS:%.c=%.o))

INCLUDEFILES=$(MBIO_DIR)/*.h

libs: libmbio.a

libmbio.a: print_msg_mbio $(MBIO_OBJS)
	$(ARCHIVER) $(EXTRA_ARCHIVE_FLAGS) ${RELEASEDIR}/${LIB} ${MBIO_OBJS}

print_msg_mbio:
	@echo "Compiling mbio library"

.PHONY: include
include: libmbio_includes

libmbio_includes:
	${CP} ${INCLUDEFILES} ${INCLUDEDIR}

clean:
	rm -rf $(MBIO_DIR)/${OUTS}
	rm -rf ${RELEASEDIR}/${LIB}

$(MBIO_DIR)/%.o: $(MBIO_DIR)/%.c $(INCLUDEFILES)
	$(COMPILER) $(COMPILER_FLAGS) $(EXTRA_COMPILER_FLAGS) $(INCLUDES) -c $< -o $@
