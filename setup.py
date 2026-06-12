from setuptools import setup, find_packages

setup(
    name="aiaudio",
    version="1.0.0",
    description="Audio Processing Meets Audio Intelligence.",
    author="AIAudio Contributors",
    python_requires=">=3.9",
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        "numpy>=1.24",
        "scipy>=1.10",
    ],
    extras_require={
        "formats": ["ffmpeg-python"],
        "gui": ["gradio>=4.0"],
        "ai": [
            "torch",
            "torchaudio",
            "openai-whisper",
            "deepfilternet",
        ],
        "dev": [
            "pytest>=7.0",
            "pytest-cov",
        ],
    },
    entry_points={
        "console_scripts": [
            "aiaudio=aiaudio.cli.main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Sound/Audio",
    ],
)
