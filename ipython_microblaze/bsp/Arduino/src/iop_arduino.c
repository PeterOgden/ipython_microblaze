#include <iop_l.h>
#include <arduino.h>

#include <xparameters.h>
#include <xsysmon.h>
#include <xgpio_l.h>
#include <xgpio.h>
#include <xiic_l.h>
#include <xtmrctr_l.h>


#define SYSMON_DEVICE_ID XPAR_SYSMON_0_DEVICE_ID

XGpio gpo;
static XSysMon SysMonInst;
XSysMon_Config *SysMonConfigPtr;
XSysMon *SysMonInstPtr = &SysMonInst;

void iop_init() {
    iop_switch_init();
    XGpio_Initialize(&gpo, XPAR_GPIO_0_DEVICE_ID);
     // SysMon Initialize
    SysMonConfigPtr = XSysMon_LookupConfig(SYSMON_DEVICE_ID);
    if(SysMonConfigPtr == NULL)
        xil_printf("SysMon LookupConfig failed.\n\r");
    unsigned int xStatus = XSysMon_CfgInitialize(SysMonInstPtr, SysMonConfigPtr,
                                    SysMonConfigPtr->BaseAddress);
    if(XST_SUCCESS != xStatus)
        xil_printf("SysMon CfgInitialize failed\r\n");
    // Clear the old status
    XSysMon_GetStatus(SysMonInstPtr);
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

static const unsigned int timer_addresses[6] = {
    XPAR_IOP3_MB3_TIMERS_SUBSYSTEM_MB3_TIMER_0_BASEADDR,
    XPAR_IOP3_MB3_TIMERS_SUBSYSTEM_MB3_TIMER_1_BASEADDR,
    XPAR_IOP3_MB3_TIMERS_SUBSYSTEM_MB3_TIMER_2_BASEADDR,
    XPAR_IOP3_MB3_TIMERS_SUBSYSTEM_MB3_TIMER_3_BASEADDR,
    XPAR_IOP3_MB3_TIMERS_SUBSYSTEM_MB3_TIMER_4_BASEADDR,
    XPAR_IOP3_MB3_TIMERS_SUBSYSTEM_MB3_TIMER_5_BASEADDR
};

void iop_pwm_generate_cycles(switch_handle h, int period, int pulse) {
    if (h < 0) return;
    unsigned int base_addr = timer_addresses[h];
    if (XTmrCtr_ReadReg(base_addr, 0, XTC_TCSR_OFFSET) != 0x296) {
        XTmrCtr_WriteReg(base_addr, 0, XTC_TCSR_OFFSET, 0x296);
        XTmrCtr_WriteReg(base_addr, 1, XTC_TCSR_OFFSET, 0x296);
    }
    XTmrCtr_WriteReg(base_addr, 0, XTC_TLR_OFFSET, period);
    XTmrCtr_WriteReg(base_addr, 1, XTC_TLR_OFFSET, pulse);
}

void iop_pwm_stop(switch_handle h) {
    if (h < 0) return;
    unsigned int base_addr = timer_addresses[h];
    XTmrCtr_WriteReg(base_addr, 0, XTC_TCSR_OFFSET, 0);
    XTmrCtr_WriteReg(base_addr, 1, XTC_TCSR_OFFSET, 0);
}

int iop_analog_read(switch_handle h) {
    return XSysMon_GetAdcData(SysMonInstPtr, XSM_CH_AUX_MIN + h);
}

int iop_analog_range(switch_handle h) {
    return 65536;
}

float iop_analog_vref(switch_handle h) {
    return 3.3f;
}

void iop_delay(unsigned int us) {
    delay_us(us);
}
