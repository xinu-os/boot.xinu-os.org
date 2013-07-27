/* Xinu Launcher
 *
 * Based on Fabrice Bellard's jslinux.js - Copyright (c) 2011-2012
 */
"use strict";

var term, pc, boot_start_time, init_state;

function term_start() {
    term = new Term(80, 30, term_handler);
    term.open();
}

/* connect terminal to serial port */
function term_handler(str) {
    pc.serial.send_chars(str);
}

/* no clipboard support ... yet */
function clipboard_error() {
    console.log("clipboard not yet supported");
}

function clipboard_set(data) {
    clipboard_error();
}

function clipboard_get(data) {
    clipboard_error();
    return "!";
}

/* provide boot time to VM */
function get_boot_time() {
    return (+new Date()) - boot_start_time;
}

/* start routine(s) for kernel */
function load_pc(kernel, mem_size) {
    init_state = {
        loader_base: 0x00010000,
        kernel_base: 0x00100000,
        kernel: kernel,
        pc_params: {
            serial_write: term.write.bind(term),
            mem_size: mem_size,
            clipboard_set: clipboard_set,
            clipboard_get: clipboard_get,
            get_boot_time: get_boot_time
        }
    };

    console.log("loader_base@0x"+init_state.loader_base.toString(16));
    console.log("kernel_base@0x"+init_state.kernel_base.toString(16));
    pc = new PCEmulator(init_state.pc_params);
    load_bootloader(0);
}

function load_bootloader(status) {
    if (status < 0) {
        console.log("error loading pc");
        return;
    }
    pc.load_binary(STATIC_URL + "kernels/jslinux/linuxstart.bin",
                   init_state.start_addr,
                   load_kernel);
}

function load_kernel(status) {
    if (status < 0) {
        console.log("error loading bootloader");
        return;
    }
    pc.load_binary(init_state.kernel, init_state.kernel_base, boot_pc);
}

function boot_pc(status) {
    if (status < 0) {
        console.log("error loading kernel");
        return;
    }

    pc.cpu.eip = init_state.loader_base;
    pc.cpu.regs[0] = init_state.pc_params.mem_size; /* EAX */
    boot_start_time = (+new Date());
    console.log("Starting Xinu on", Date(boot_start_time));
    pc.start();
}

term_start();
