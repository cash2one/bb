#include <Python.h>

#define MAP_MAX 10

static short *m[MAP_MAX];

static PyObject* t1(PyObject* self, PyObject* args) {
	//printf("%lx, %lx", self, args);
	printf("%lu, %lu\n", sizeof(m), sizeof(m[0][0]));
	int i = m[0][0];
	for (i = 0; i < MAP_MAX; i++) {
		m[i] = calloc(sizeof(short), 8196);
		//printf("%ld\n", m[i]);
	}
	return PyLong_FromLong(1);
}

PyObject* t2(PyObject* self, PyObject* args, PyObject* kwargs) {
	//printf("%lx, %lx", self, args);
	return PyLong_FromLong(2);
}

static PyMethodDef methods[] = {
	{"f1",  t1, METH_VARARGS, "doc1, 一"},
	//{"f2",  t2, METH_VARARGS | METH_KEYWORDS, "doc2"},
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
PyInit_t(void) {
	printf("init!\n");
	return PyModule_Create(&speedupsmodule);
}
