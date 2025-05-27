from deblur_gs import train

train.main([
    "-s", "/path/to/colmap",
    "-m", "/path/to/model",
    "-i", "/path/to/frames",
    "--iterations", "3000",
    "--test_iterations", "-1"
])
