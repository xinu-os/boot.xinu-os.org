/*
   PC Emulater wrapper

   Copyright (c) 2012 Fabrice Bellard
   Minor modifications Copyright (c) 2013 Michael Schultz

   Redistribution or commercial use is prohibited without the author's
   permission.
*/
"use strict";

function test_typed_arrays()
{
    return (window.Uint8Array &&
            window.Uint16Array &&
            window.Int32Array &&
            window.ArrayBuffer);
}

if (test_typed_arrays()) {
    include(STATIC_URL + "kernels/jslinux/cpux86-ta.js");
} else {
    include(STATIC_URL + "kernels/jslinux/cpux86-std.js");
    document.write('<canvas id="dummy_canvas" width="1" height="1"></canvas>');
}
