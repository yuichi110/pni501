#ifndef PNI501_EXTRA_BINDING_COMMON_H
#define PNI501_EXTRA_BINDING_COMMON_H

#define Py_LIMITED_API 0x030a0000
#include <Python.h>

typedef struct TSLanguage TSLanguage;

#define PNI_CAT2(a, b) a##b
#define PNI_CAT(a, b) PNI_CAT2(a, b)
#define PNI_STR2(x) #x
#define PNI_STR(x) PNI_STR2(x)

#define TS_LANG_FUNC PNI_CAT(tree_sitter_, TS_LANG_ID)
#define PY_MOD_INIT PNI_CAT(PyInit__, TS_LANG_ID)
#define PY_MOD_NAME PNI_STR(PNI_CAT(_, TS_LANG_ID))

extern const TSLanguage *TS_LANG_FUNC(void);

static PyObject *_pni_binding_language(PyObject *self, PyObject *args) {
    (void)self;
    (void)args;
    return PyCapsule_New((void *)TS_LANG_FUNC(), "tree_sitter.Language", NULL);
}

static PyMethodDef _pni_methods[] = {
    {"language", _pni_binding_language, METH_NOARGS, "Return the Tree-sitter Language PyCapsule."},
    {NULL, NULL, 0, NULL},
};

static struct PyModuleDef _pni_module = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = PY_MOD_NAME,
    .m_doc = NULL,
    .m_size = -1,
    .m_methods = _pni_methods,
};

PyMODINIT_FUNC PY_MOD_INIT(void) {
    return PyModule_Create(&_pni_module);
}

#endif
