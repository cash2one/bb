#include <Python.h>

static PyObject* test(PyObject* self, PyObject* args) {
	printf("%x, %x", self, args);
	return PyLong_FromLong(123);
}

static PyMethodDef methods[] = {
	{"f",  test, METH_VARARGS, ""},
	{NULL, NULL, 0, NULL}
};

static struct PyModuleDef speedupsmodule = {
	PyModuleDef_HEAD_INIT,
	"t",
	NULL,
	-1,
	methods
};

PyMODINIT_FUNC
PyInit_t() {
	return PyModule_Create(&speedupsmodule);
}
