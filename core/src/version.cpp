#include "naturo/exports.h"

static const char* NATURO_VERSION = "0.1.0";
static bool g_initialized = false;

extern "C" {

NATURO_API const char* naturo_version(void) {
    return NATURO_VERSION;
}

NATURO_API int naturo_init(void) {
    if (g_initialized) return 0;
    g_initialized = true;
    return 0;  // success
}

NATURO_API int naturo_shutdown(void) {
    if (!g_initialized) return 0;
    g_initialized = false;
    return 0;  // success
}

}
