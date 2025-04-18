import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import multivariate_normal

def gs(poses, points, sigma=0.1):
    point_cloud = []

    for image_name, pose in poses.items():
        position = np.array(pose['position'])
        rotation = np.array(pose['rotation'])

        for point in points:
            point_position = np.array(point['xyz'])

            dist = np.linalg.norm(position - point_position)
            gaussian_point = multivariate_normal.pdf(dist, mean=0, cov=sigma)

            point_cloud.append({
                'position': point_position,
                'intensity': gaussian_point  # Gaussian 점의 강도
            })

    return point_cloud

def pc(point_cloud):
    positions = np.array([point['position'] for point in point_cloud])
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    ax.scatter(positions[:, 0], positions[:, 1], positions[:, 2], s=0.5)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    plt.show()
