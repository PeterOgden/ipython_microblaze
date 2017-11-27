#include <iop.h>
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

__attribute__((constructor(1000)))
void iop_switch_init() {
    commit_assignments();
    timer delay_timer = timer_open(5);
    timer_set_as_default(delay_timer, 1);
}

gpio gpio_open_iop_pin(unsigned char pin) {
    digital_pins[pin] = D_GPIO;
    commit_assignments();
    return gpio_open_pin(XPAR_IOP3_MB3_GPIO_SUBSYSTEM_MB3_ARDUINO_GPIO_D13_D0_A5_A0_DEVICE_ID, 0, pin);
}
gpio gpio_open_iop_grove(unsigned char port, unsigned char wire) {
    return gpio_open_iop_pin(pin_offsets[port] + wire);
}

static const unsigned char adc_offset[6] = {
    1, 9, 6, 15, 5, 13
};

analog analog_open_iop_pin(unsigned char pin) {
    analog_pins[pin] = A_GPIO;
    commit_assignments();
    return analog_open(adc_offset[pin]);
}
analog analog_open_iop_grove(unsigned char port, unsigned char wire) {
    return analog_open_iop_pin(analog_offsets[port] + wire);
}

// D3, D5, D6, D9, D10, D11
static const char pwm_offsets[14] = {
    -1, -1, -1, 0, -1, 1, 2,
    -1, -1, 3, 4, 5, -1, -1
};

timer timer_open_iop_pin(unsigned char pin) {
    char offset = pwm_offsets[pin];
    if (offset == -1) return ASSIGN_FAILED;
    digital_pins[pin] = D_PWM;
    commit_assignments();
    return timer_open(offset);
}

timer timer_open_iop_grove(unsigned char port, unsigned char wire) {
    return timer_open_iop_pin(pin_offsets[port] + wire);
}

i2c i2c_open_iop_pins(unsigned char scl, unsigned char sda) {
    return i2c_open(XPAR_IOP3_MB3_IIC_SUBSYSTEM_MB3_IIC_PL_SW_DEVICE_ID);
}
i2c i2c_open_iop_grove(unsigned char port) {
    return i2c_open(XPAR_IOP3_MB3_IIC_SUBSYSTEM_MB3_IIC_PL_SW_DEVICE_ID);
}
