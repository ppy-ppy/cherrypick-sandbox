language: PYTHON
name: "template"

variable {
    name: "vcpus"
    type: INT
    size: 1
    min: 1
    max: 16
}

variable {
    name: "ram"
    type: INT
    size: 1
    min: 1
    max: 32
}

variable {
    name: "disk"
    type: INT
    size: 1
    min: 1
    max: 160
}

variable {
    name: "machine_count"
    type: INT
    size: 1
    min: 4
    max: 20
}

