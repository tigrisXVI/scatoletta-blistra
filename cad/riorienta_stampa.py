import trimesh, numpy as np, sys, glob
def appoggio(m):
    zmin = m.bounds[0][2]; c = m.triangles_center[:, 2] < zmin + 0.05
    n = m.face_normals[:, 2] < -0.99
    return m.area_faces[c & n].sum()
for f in sys.argv[1:]:
    m = trimesh.load(f); e = m.extents
    if e[2] <= min(e[0], e[1]) + 0.01 or min(e) > 8 or sorted(e)[1] < 30: continue
    ax = int(np.argmin(e)); best = None
    for s in (1, -1):
        v = np.zeros(3); v[ax] = s
        R = trimesh.geometry.align_vectors(v, [0, 0, -1])
        mm = m.copy(); mm.apply_transform(R)
        a = appoggio(mm)
        if best is None or a > best[0]: best = (a, mm)
    mm = best[1]; b = mm.bounds; mm.apply_translation([-(b[0][0] + b[1][0]) / 2, -(b[0][1] + b[1][1]) / 2, -b[0][2]])
    mm.export(f); print("riorientato", f.split('/')[-1], [round(x) for x in e], "->", [round(x) for x in mm.extents], "appoggio", round(best[0]), "mm2")
