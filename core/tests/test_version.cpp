#include "naturo/exports.h"
#include <cstring>
#include <cstdio>

int main() {
    int failed = 0;

    // Test version string
    const char* ver = naturo_version();
    if (!ver || strlen(ver) == 0) {
        printf("FAIL: naturo_version() returned empty\n");
        failed++;
    } else {
        printf("PASS: naturo_version() = %s\n", ver);
    }

    // Test init
    int rc = naturo_init();
    if (rc != 0) {
        printf("FAIL: naturo_init() returned %d\n", rc);
        failed++;
    } else {
        printf("PASS: naturo_init() = 0\n");
    }

    // Test double init (should be safe)
    rc = naturo_init();
    if (rc != 0) {
        printf("FAIL: naturo_init() second call returned %d\n", rc);
        failed++;
    } else {
        printf("PASS: naturo_init() idempotent\n");
    }

    // Test shutdown
    rc = naturo_shutdown();
    if (rc != 0) {
        printf("FAIL: naturo_shutdown() returned %d\n", rc);
        failed++;
    } else {
        printf("PASS: naturo_shutdown() = 0\n");
    }

    printf("\n%s: %d tests failed\n", failed ? "FAILED" : "ALL PASSED", failed);
    return failed;
}
