#include <iop_switch.h>
#include <pmod.h>
#include <mbio.h>

static unsigned char grove_port_map[4][2] = {
    {0, 4}, {1, 5}, {7, 3}, {6, 2}
};

static char assignments[16];
static char uses[16];
static char initialised;

void iop_switch_init() {
    if (initialised) return;
    for (int i = 0; i < 16; ++i) {
        assignments[i] = i;
        uses[i] = i;
    }
    mb_io_init();
    mb_timer delay_timer = mb_timer_open(0);
    mb_set_delay_timer(delay_timer, 1);
    initialised = 1;
}

static void commit_assignments() {
    config_pmod_switch(
        assignments[0],
        assignments[1],
        assignments[2],
        assignments[3],
        assignments[4],
        assignments[5],
        assignments[6],
        assignments[7]
    );
}

static void assign_connection(unsigned char input, unsigned char output) {
    if (assignments[input] == output) return;
    char prev_output = assignments[input];
    char prev_input = uses[output];
    assignments[prev_input] = prev_output;
    uses[prev_output] = prev_input;
    assignments[input] = output;
    uses[output] = input;
}

mb_i2c iop_switch_i2c_raw(unsigned char scl, unsigned char sda) {
    assign_connection(scl, SCL);
    assign_connection(sda, SDA);
    commit_assignments();
    return mb_i2c_open(0);
}

mb_i2c iop_switch_i2c_grove(unsigned char port) {
    return iop_switch_i2c_raw(grove_port_map[port][0], grove_port_map[port][1]);
}

mb_gpio iop_switch_gpio_raw(unsigned char pin) {
    assign_connection(pin, pin);
    commit_assignments();
    return mb_gpio_open_pin(0, 0, pin);
}

mb_gpio iop_switch_gpio_grove(unsigned char port, unsigned char wire) {
    return iop_switch_gpio_raw(grove_port_map[port][wire]);
}

mb_timer iop_switch_pwm_raw(unsigned char pin) {
    assign_connection(pin, PWM);
    commit_assignments();
    return mb_timer_open(0);
}

mb_timer iop_switch_pwm_grove(unsigned char port, unsigned char wire) {
    return iop_switch_pwm_raw(grove_port_map[port][wire]);
}

mb_adc iop_switch_analog_raw(unsigned char pin) {
    return -1;
}

mb_adc iop_switch_analog_grove(unsigned char port, unsigned char wire) {
    return -1;
}

