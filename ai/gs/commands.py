import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import multivariate_normal

def create_gaussian_point_cloud(poses, points, sigma=0.1):
    point_cloud = []

    for image_name, pose in poses.items():
        position = np.array(pose['position'])
        rotation = np.array(pose['rotation'])

        # 각 이미지에서의 카메라 위치와 회전 정보를 기반으로 Gaussian 점 생성
        for point in points:
            point_position = np.array(point['xyz'])

            # 카메라 위치와 3D 점을 기준으로 Gaussian 분포를 생성
            dist = np.linalg.norm(position - point_position)  # 카메라 위치와 점 간 거리 계산
            gaussian_point = multivariate_normal.pdf(dist, mean=0, cov=sigma)  # 가우시안 함수 사용

            point_cloud.append({
                'position': point_position,
                'intensity': gaussian_point  # Gaussian 점의 강도
            })

    return point_cloud

def visualize_point_cloud(point_cloud):
    positions = np.array([point['position'] for point in point_cloud])
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    ax.scatter(positions[:, 0], positions[:, 1], positions[:, 2], s=0.5)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    plt.show()
