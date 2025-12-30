import os

def opencv_orb_match_score(path_a, path_b, max_features=500):
    """Return a match score between two images using OpenCV ORB descriptors.

    Score is the number of "good" matches (ratio test) found — higher means
    more similar. If OpenCV is not installed or processing fails, returns None.
    """
    try:
        import cv2
    except Exception:
        return None

    try:
        img1 = cv2.imread(path_a, cv2.IMREAD_GRAYSCALE)
        img2 = cv2.imread(path_b, cv2.IMREAD_GRAYSCALE)
        if img1 is None or img2 is None:
            return None

        # create ORB detector
        orb = cv2.ORB_create(nfeatures=max_features)
        kp1, des1 = orb.detectAndCompute(img1, None)
        kp2, des2 = orb.detectAndCompute(img2, None)
        if des1 is None or des2 is None:
            return 0

        # BFMatcher with Hamming distance for ORB
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
        matches = bf.knnMatch(des1, des2, k=2)

        # Apply ratio test (Lowe's ratio)
        good = []
        for m_n in matches:
            if len(m_n) != 2:
                continue
            m, n = m_n
            if m.distance < 0.75 * n.distance:
                good.append(m)

        return len(good)
    except Exception:
        return None
