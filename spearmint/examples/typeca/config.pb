language: PYTHON
name: "typeca"

variable {
    name: "vm_type"
    type: ENUM
    size: 1
    options: "m1"
    options: "r2"
    options: "c3"
}

variable {
    name: "vm_size"
    type: ENUM
    size: 1
    options: "small"
    options: "medium"
    options: "large"
    options: "xlarge"
}

variable {
    name: "machine_count"
    type: INT
    size: 1
    min: 2
    max: 16
}

