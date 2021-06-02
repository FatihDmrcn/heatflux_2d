import numpy as np


def coefficient_diagonal_matrix(width, height, alpha, beta, gamma, bc_vector):
    n = width * height
    coefficient_matrix = np.zeros((n, n), dtype=float)

    diagonals = [[gamma] * n, [alpha] * (n-1), [beta] * (n - width)]

    coefficient_matrix += np.diag(diagonals[0], 0)
    coefficient_matrix += np.diag(diagonals[1], -1)
    coefficient_matrix += np.diag(diagonals[1], +1)
    coefficient_matrix += np.diag(diagonals[2], -width)
    coefficient_matrix += np.diag(diagonals[2], +width)

    for i, bc in enumerate(bc_vector, 0):
        if bc != 'F':
            coefficient_matrix[i, :] = 0

    return coefficient_matrix


if __name__ == "__main__":
    x = 4
    y = 4
    bc_field = np.zeros((y, x), dtype=str)
    bc_field[1:-1, 1:-1] = 'F'
    U = coefficient_diagonal_matrix(x, y, 1, 2, 3, bc_field.flatten())
    I = np.eye(y*x)
    v = [1]*(x*y)
    A = np.dot(U,v)

    print(U)
    print(A)
