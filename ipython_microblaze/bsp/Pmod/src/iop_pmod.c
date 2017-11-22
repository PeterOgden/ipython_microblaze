#include <iop_l.h>
#include <pmod.h>

#include <xparameters.h>
#include <xgpio_l.h>
#include <xgpio.h>
#include <xiic_l.h>
#include <xtmrctr_l.h>

XGpio gpo;

void iop_init() {
    iop_switch_init();
    XGpio_Initialize(&gpo, XPAR_GPIO_0_DEVICE_ID);
}

void iop_i2c_write(switch_handle h, unsigned int addr, unsigned char* data, unsigned char length) {
    XIic_Send(XPAR_IIC_0_BASEADDR, addr, data, length, XIIC_STOP);
}

void iop_i2c_read(switch_handle h, unsigned int addr, unsigned char* data, unsigned char length) {
    XIic_Recv(XPAR_IIC_0_BASEADDR, addr, data, length, XIIC_STOP);
}

static unsigned int values = 0;
static unsigned int tristate = 0;

int iop_gpio_read(switch_handle h) {
    unsigned int v = XGpio_DiscreteRead(&gpo, 1);
    return (v >> h) & 1;   
}

void iop_gpio_write(switch_handle h, unsigned char value) {
    unsigned m = 1 << h;
    if (value) {
        values |= m;
    } else {
        values &= ~m;
    }
    XGpio_DiscreteWrite(&gpo, 1, values);
}

void iop_gpio_set_direction(switch_handle h, unsigned char direction) {
    unsigned int m = 1 << h;
    if (direction) {
        tristate |= m;
    } else {
        tristate &= ~m;
    }
    XGpio_SetDataDirection(&gpo, 1, tristate);
}

void iop_pwm_generate_cycles(switch_handle h, int period, int pulse) {
    unsigned int base_addr = XPAR_IOP1_MB1_TIMER_BASEADDR;
    if (XTmrCtr_ReadReg(base_addr, 0, XTC_TCSR_OFFSET) != 0x296) {
        XTmrCtr_WriteReg(base_addr, 0, XTC_TCSR_OFFSET, 0x296);
        XTmrCtr_WriteReg(base_addr, 1, XTC_TCSR_OFFSET, 0x296);
    }
    XTmrCtr_WriteReg(base_addr, 0, XTC_TLR_OFFSET, period);
    XTmrCtr_WriteReg(base_addr, 1, XTC_TLR_OFFSET, pulse);
}

void iop_pwm_stop(switch_handle h) {
    unsigned int base_addr = XPAR_IOP1_MB1_TIMER_BASEADDR;
    XTmrCtr_WriteReg(base_addr, 0, XTC_TCSR_OFFSET, 0);
    XTmrCtr_WriteReg(base_addr, 1, XTC_TCSR_OFFSET, 0);
}

int iop_analog_read(switch_handle h) {
    return 0;
}

int iop_analog_range(switch_handle h) {
    return 0;
}

float iop_analog_vref(switch_handle h) {
    return 0;
}

void iop_delay(unsigned int us) {
    delay_us(us);
}
