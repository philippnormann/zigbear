from setuptools import setup

setup(
    name="zigbear",
    version="0.1.0",
    description="A curious bear looking for some ZigBee honey 🐻🐝",
    author="Philipp Normann, Marc Mettke, Torben Tietgen",
    url="https://github.com/philippnormann1337/zigbear",
    install_requires=[
        "cffi==1.13.2",
        "cryptography==2.8",
        "parse==1.14.0",
        "pycparser==2.19",
        "pycryptodomex==3.9.6",
        "pyserial==3.4",
        "scapy==2.4.3",
        "six==1.14.0",
    ],
    packages=["zigbear"],
)
