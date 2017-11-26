#include <iop_switch.h>
#include <arduino.h>
#include <mbio.h>

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
    mb_io_init();
    commit_assignments();
    mb_timer delay_timer = mb_timer_open(5);
    mb_set_delay_timer(delay_timer, 1);
}

mb_gpio iop_switch_gpio_raw(unsigned char pin) {
    digital_pins[pin] = D_GPIO;
    commit_assignments();
    return mb_gpio_open_pin(XPAR_IOP3_MB3_GPIO_SUBSYSTEM_MB3_ARDUINO_GPIO_D13_D0_A5_A0_DEVICE_ID, 0, pin);
}
mb_gpio iop_switch_gpio_grove(unsigned char port, unsigned char wire) {
    return iop_switch_gpio_raw(pin_offsets[port] + wire);
}

static const unsigned char adc_offset[6] = {
    1, 9, 6, 15, 5, 13
};

mb_adc iop_switch_analog_raw(unsigned char pin) {
    analog_pins[pin] = A_GPIO;
    commit_assignments();
    return mb_adc_open(adc_offset[pin]);
}
mb_adc iop_switch_analog_grove(unsigned char port, unsigned char wire) {
    return iop_switch_analog_raw(analog_offsets[port] + wire);
}

// D3, D5, D6, D9, D10, D11
static const char pwm_offsets[14] = {
    -1, -1, -1, 0, -1, 1, 2,
    -1, -1, 3, 4, 5, -1, -1
};

mb_timer iop_switch_pwm_raw(unsigned char pin) {
    char offset = pwm_offsets[pin];
    if (offset == -1) return ASSIGN_FAILED;
    digital_pins[pin] = D_PWM;
    commit_assignments();
    return mb_timer_open(offset);
}

mb_timer iop_switch_pwm_grove(unsigned char port, unsigned char wire) {
    return iop_switch_pwm_raw(pin_offsets[port] + wire);
}

mb_i2c iop_switch_i2c_raw(unsigned char scl, unsigned char sda) {
    return mb_i2c_open(XPAR_IOP3_MB3_IIC_SUBSYSTEM_MB3_IIC_PL_SW_DEVICE_ID);
}
mb_i2c iop_switch_i2c_grove(unsigned char port) {
    return mb_i2c_open(XPAR_IOP3_MB3_IIC_SUBSYSTEM_MB3_IIC_PL_SW_DEVICE_ID);
}
