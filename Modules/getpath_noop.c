/* Implements the getpath API for compiling with no functionality */

#include "MyFRpy.h"
#include "pycore_pathconfig.h"

PyStatus
_PyConfig_InitPathConfig(PyConfig *config, int compute_path_config)
{
    return PyStatus_Error("path configuration is unsupported");
}
