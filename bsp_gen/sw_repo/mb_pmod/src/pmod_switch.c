#include <iop.h>
#include <pmod.h>
#include <mbio.h>

static unsigned char grove_port_map[4][2] = {
    {0, 4}, {1, 5}, {7, 3}, {6, 2}
};

static char assignments[16];
static char uses[16];

__attribute__((constructor(1000)))
void iop_switch_init() {
    for (int i = 0; i < 16; ++i) {
        assignments[i] = i;
        uses[i] = i;
    }
    timer delay_timer = timer_open(0);
    timer_set_as_default(delay_timer, 1);
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

i2c i2c_open_iop_pins(unsigned char scl, unsigned char sda) {
    assign_connection(scl, SCL);
    assign_connection(sda, SDA);
    commit_assignments();
    return i2c_open(0);
}

i2c i2c_open_iop_grove(unsigned char port) {
    return i2c_open_iop_pins(grove_port_map[port][0], grove_port_map[port][1]);
}

gpio gpio_open_iop_pin(unsigned char pin) {
    assign_connection(pin, pin);
    commit_assignments();
    return gpio_open_pin(0, 0, pin);
}

gpio gpio_open_iop_grove(unsigned char port, unsigned char wire) {
    return gpio_open_iop_pin(grove_port_map[port][wire]);
}

timer timer_open_iop_pin(unsigned char pin) {
    assign_connection(pin, PWM);
    commit_assignments();
    return timer_open(0);
}

timer timer_open_iop_grove(unsigned char port, unsigned char wire) {
    return timer_open_iop_pin(grove_port_map[port][wire]);
}

analog analog_open_iop_pin(unsigned char pin) {
    return -1;
}

analog analog_open_iop_grove(unsigned char port, unsigned char wire) {
    return -1;
}

