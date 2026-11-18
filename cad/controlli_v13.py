"""Controlli della v1.3: gli stessi della v1.2 (cad/controlli_v12.py) sul modello v1.3.
La ruota destra e' la sinistra girata di mezzo giro: gira nel verso opposto."""
import sys
import scatoletta_v13 as s13
import scatoletta_v12 as s12
import croce_check_v10 as croce_check
_ang = croce_check.angolo_ruota
croce_check.angolo_ruota = lambda M, i, phi: (-_ang(M, i, phi) if i == 1 else _ang(M, i, phi))
s12.Modello12 = s13.Modello13            # controlli_v12 costruisce s12.Modello12: qui e' la v1.3
import controlli_v12

if __name__ == "__main__":
    ok = controlli_v12.controlla("2m")
    print("RISULTATO v1.3:", "ok" if ok else "DA CORREGGERE")
    sys.exit(0 if ok else 1)
