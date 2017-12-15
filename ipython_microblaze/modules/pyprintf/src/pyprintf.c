#include <unistd.h>
#include <pyprintf.h>
#include <string.h>
#include <stdarg.h>

static const char printf_command = 1;

void pyprintf(const char* format, ...) {
    unsigned short len = strlen(format);
    write(3, &printf_command, 1);
    write(3, &len, 2);
    write(3, format, len);
    int in_special = 0;
    va_list args;
    va_start(args, format);
    while (*format != '\0') {
        if (in_special) {
            switch (*format) {
            case 'd':
            {
                int val = va_arg(args, int);
                write(3, &val, sizeof(val));
            }
                break;
            case 'f':
            {
                float val = (double)va_arg(args, double);
                write(3, &val, sizeof(val));
            }
                break;
            }
            in_special = 0;
        } else if (*format == '%') {
            in_special = 1;
        }
        ++format;
    }
}
