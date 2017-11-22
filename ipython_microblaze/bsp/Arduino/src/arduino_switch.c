#include <iop_switch.h>
#include <arduino.h>
#include <arduino_io_switch.h>

char analog_pins[6];
char uart_pin;
char digital_pins[14];

static char pin_offsets[7] = {
    2, 3, 4, 6, 8, 10, 12
};

static char analog_offsets[4] = {
    0, 2, 3, 4
};

static void commit_assignments() {
    config_arduino_switch(
        analog_pins[0],
        analog_pins[1],
        analog_pins[2],
        analog_pins[3],
        analog_pins[4],
        analog_pins[5],
        uart_pin,
        digital_pins[2],
        digital_pins[3],
        digital_pins[4],
        digital_pins[5],
        digital_pins[6],
        digital_pins[7],
        digital_pins[8],
        digital_pins[9],
        digital_pins[10],
        digital_pins[11],
        digital_pins[12],
        digital_pins[13]
    );

}

void iop_switch_init() {
    arduino_init(0, 0, 0, 0);
    commit_assignments();
}

switch_handle iop_switch_gpio_raw(unsigned char pin) {
    digital_pins[pin] = D_GPIO;
    commit_assignments();
    return pin;
}
switch_handle iop_switch_gpio_grove(unsigned char port, unsigned char wire) {
    return iop_switch_gpio_raw(pin_offsets[port] + wire);
}

static const switch_handle adc_offset[6] = {
    1, 9, 6, 15, 5, 13
};

switch_handle iop_switch_analog_raw(unsigned char pin) {
    analog_pins[pin] = A_GPIO;
    commit_assignments();
    return adc_offset[pin];
}
switch_handle iop_switch_analog_grove(unsigned char port, unsigned char wire) {
    return iop_switch_analog_raw(analog_offsets[port] + wire);
}

// D3, D5, D6, D9, D10, D11
static const char pwm_offsets[14] = {
    -1, -1, -1, 0, -1, 1, 2,
    -1, -1, 3, 4, 5, -1, -1
};

switch_handle iop_switch_pwm_raw(unsigned char pin) {
    char offset = pwm_offsets[pin];
    if (offset == -1) return ASSIGN_FAILED;
    digital_pins[pin] = D_PWM;
    commit_assignments();
    return offset;
}

switch_handle iop_switch_pwm_grove(unsigned char port, unsigned char wire) {
    return iop_switch_pwm_raw(pin_offsets[port] + wire);
}

switch_handle iop_switch_i2c_raw(unsigned char scl, unsigned char sda) {
    return 0;
}
switch_handle iop_switch_i2c_grove(unsigned char port) {
    return 0;
}
