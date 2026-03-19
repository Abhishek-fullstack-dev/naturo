#ifndef NATURO_EXPORTS_H
#define NATURO_EXPORTS_H

#ifdef _WIN32
    #ifdef NATURO_BUILDING
        #define NATURO_API __declspec(dllexport)
    #else
        #define NATURO_API __declspec(dllimport)
    #endif
#else
    #define NATURO_API __attribute__((visibility("default")))
#endif

#ifdef __cplusplus
extern "C" {
#endif

// Version
NATURO_API const char* naturo_version(void);

// Init / Shutdown
NATURO_API int naturo_init(void);
NATURO_API int naturo_shutdown(void);

// Future APIs will be added here as we implement them:
// - naturo_capture_*
// - naturo_list_*
// - naturo_find_*
// - naturo_click_*
// - naturo_type_*
// etc.

#ifdef __cplusplus
}
#endif

#endif // NATURO_EXPORTS_H
