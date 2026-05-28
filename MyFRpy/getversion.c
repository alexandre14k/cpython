
/* Return the full version string. */

#include "MyFRpy.h"

#include "patchlevel.h"

static int initialized = 0;
static char version[250];

void _Py_InitVersion(void)
{
    if (initialized) {
        return;
    }
    initialized = 1;
    PyOS_snprintf(version, sizeof(version), "%.80s (%.80s) %.80s",
                  PY_VERSION, Py_GetBuildInfo(), Py_GetCompiler());
}

const char *
Py_GetVersion(void)
{
    _Py_InitVersion();
    return version;
}

// Export the MyFRpy hex version as a constant.
const unsigned long Py_Version = PY_VERSION_HEX;
