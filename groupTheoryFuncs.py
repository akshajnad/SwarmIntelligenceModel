#dihedral group
import numpy as np

def apply_translation(swarm, v):
    """
    Applies uniform translation to all agents.
    :param swarm: List of ship positions (x, y).
    :param v: Translation vector (vx, vy).
    """
    for i in range(len(swarm)):
        swarm[i][0] += v[0]  # Translate x
        swarm[i][1] += v[1]  # Translate y
    return swarm

def rotation_matrix(theta):
    """
    Constructs a 2D rotation matrix for angle theta.
    """
    return np.array([[np.cos(theta), -np.sin(theta)],
                     [np.sin(theta), np.cos(theta)]])

def apply_rotation(swarm, center, k, n):
    """
    Applies rotational symmetry based on Dihedral group.
    :param swarm: List of ship positions (x, y).
    :param center: Center of rotation (cx, cy).
    :param k: Rotation index.
    :param n: Total number of symmetry elements.
    """
    theta = (2 * np.pi * k) / n
    Rk = rotation_matrix(theta)
    for i in range(len(swarm)):
        pos = np.array([swarm[i][0], swarm[i][1]]) - np.array(center)
        new_pos = np.dot(Rk, pos) + np.array(center)
        swarm[i] = [int(round(new_pos[0])), int(round(new_pos[1]))]
    return swarm

def reflection_matrix():
    """
    Constructs a reflection matrix.
    """
    return np.array([[1, 0],
                     [0, -1]])

def apply_reflection(swarm, center, k, n):
    """
    Applies reflection symmetry based on Dihedral group.
    :param swarm: List of ship positions (x, y).
    :param center: Center of reflection (cx, cy).
    :param k: Reflection index.
    :param n: Total number of symmetry elements.
    """
    theta = (2 * np.pi * k) / n
    Sk = reflection_matrix()
    for i in range(len(swarm)):
        pos = np.array([swarm[i][0], swarm[i][1]]) - np.array(center)
        rotated_pos = np.dot(rotation_matrix(theta), pos)
        reflected_pos = np.dot(Sk, rotated_pos) + np.array(center)
        swarm[i] = [int(round(reflected_pos[0])), int(round(reflected_pos[1]))]
    return swarm

def apply_cyclic_movement(swarm, alpha, n):
    """
    Applies cyclic group-based movement to the swarm.
    :param swarm: List of ship positions (x, y).
    :param alpha: Step size for movement.
    :param n: Number of elements in the cyclic group.
    """
    for i in range(len(swarm)):
        k = (i + 1) % n
        M_gk = np.array([np.cos((2 * np.pi * k) / n), np.sin((2 * np.pi * k) / n)])
        swarm[i][0] += int(round(alpha * M_gk[0]))  # Update x position
        swarm[i][1] += int(round(alpha * M_gk[1]))  # Update y position
    return swarm
