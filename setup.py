from setuptools import setup

setup(
    name="zigbear",
    version="0.1.0",
    description="A curious bear looking for some ZigBee honey 🐻🐝",
    author="Philipp Normann, Marc Mettke, Torben Tietgen",
    url="https://github.com/philippnormann1337/ZigBear",
    install_requires=["pycryptodomex==3.9.4", "pyserial==3.4", "scapy==2.4.3"],
    packages=["zigbear"],
)
