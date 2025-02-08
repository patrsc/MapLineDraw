export function findNearestIndexOnLine(points, lat, lon) {
    // Find index i of a polyline P, such that point (lat, lon) is almost inbetween P[i] and P[i+1]
    let insertIndex = 0
    let minDistance = Infinity
    const p = latLonToXY({ lat, lon })
    for (let i = 0; i < points.length - 1; i++) {
        const p1 = latLonToXY(points[i])
        const p2 = latLonToXY(points[i + 1])
        const d = pointSegmentDistance(p1, p2, p)
        if (d < minDistance) {
            minDistance = d
            insertIndex = i
        }
    }
    return insertIndex
}

/**
 * Calculates the minimum normal distance from a point to a line segment
 * and the normalized position of the closest point on the line segment.
 *
 * @param {Object} p1 - The first endpoint of the line segment ({x, y}).
 * @param {Object} p2 - The second endpoint of the line segment ({x, y}).
 * @param {Object} p - The point to measure distance from ({x, y}).
 * @returns {Object} An object containing:
 *   - distance {number}: The shortest distance from point p to the line segment.
 *   - t {number}: The normalized position along the line segment where
 *                 the perpendicular projection occurs (0 at p1, 1 at p2).
 *                 Values outside [0,1] indicate projections beyond the segment.
 */
export function pointLineDistance(p1, p2, p) {
    // Vector from p1 to p2
    let dx = p2.x - p1.x;
    let dy = p2.y - p1.y;
    
    // Vector from p1 to p
    let px = p.x - p1.x;
    let py = p.y - p1.y;
    
    // Compute the projection scalar (normalized position on the line)
    let dotProduct = px * dx + py * dy;
    let lenSq = dx * dx + dy * dy;
    let t = dotProduct / lenSq;

    // Compute the closest point on the infinite line
    let closestX = p1.x + t * dx;
    let closestY = p1.y + t * dy;

    // Compute the minimum distance
    let distX = p.x - closestX;
    let distY = p.y - closestY;
    let distance = Math.sqrt(distX * distX + distY * distY);

    return { distance, t };
}

export function pointSegmentDistance(p1, p2, p) {
    const { distance, t } = pointLineDistance(p1, p2, p)
    if (t < 0) {
        // distance to p1
        return pointDistance(p1, p)
    } else if (t > 1) {
        // distance to p2
        return pointDistance(p2, p)
    }
    return distance
}

export function pointDistance(p1, p2) {
    let dx = p2.x - p1.x;
    let dy = p2.y - p1.y;
    return Math.sqrt(dx * dx + dy * dy)
}

function latLonToXY(p) {
    // this approximation (although wrong) is sufficient for finding the closest point
    return { x: p.lon, y: p.lat }
}
