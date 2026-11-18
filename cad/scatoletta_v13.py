#!/usr/bin/env python3
"""
Scatoletta Blistra v1.3 (dalla v1.2): piu' stretta, caroselli che sporgono.

  - SIMMETRIA A MEZZO GIRO: il lato destro e' il sinistro girato di 180 gradi attorno all'asse verticale.
      dietro in alto  -> stepper e croce della ruota SINISTRA + ricarica dall'alto della ruota SINISTRA
      davanti in alto -> stepper e croce della ruota DESTRA   + ricarica dall'alto della ruota DESTRA
    (nella v1.2 i due stepper stavano tutti e due dietro e la ricarica tutta davanti)
  - STEPPER GIRATI VERSO IL CENTRO: la faccia con l'albero guarda la propria ruota, il corpo passa sopra l'altra
    ruota (dove nella v1.2 c'era l'altra meta' della ricarica). Niente sporge piu' verso i fianchi.
  - guscio largo come la v1.0 (Y_DX = 26,45: 52,9 mm invece di 64,2)
  - cassette con una CORNICE che esce di 2 mm dal fianco: niente piu' pozzetto attorno alla ruota
  - display OLED spostato davanti, sotto le ruote (in alto davanti c'e' la croce della ruota destra)
  - nella camera dietro: ULN2003 spostati verso il centro, HX711 a destra, ESP32 piu' in alto (sopra gli ULN2003)

Assi: X davanti, Y destra-sinistra (asse delle ruote), Z in alto. mm.
"""
import math, os
from manifold3d import Manifold, CrossSection
import scatoletta_v10 as s10
import scatoletta_v12 as s12
import scatoletta_v5 as v5
from scatoletta_v3 import cil, scatola, cil_x, cil_y, ruota, ccw, a_mesh
from scatoletta_v10 import N, PASSO, PARETE, R_SPIG, R_TOP, MOD, Z_PIGN_G, Z_CROCE, D_ASSE, Z_TORRE, G_FERMO, stampa, VERSI
from scatoletta_v12 import K, STEP, FC, RA, OLED, Z_NASTRO, Z_SUONO, D_MOT, A_MOT, doppio_d

# ---- la cassetta "tipo sinistro" ha l'ingresso della ricarica DIETRO (la destra, girata, ce l'ha davanti)
s10.ANG_RICARICA = 180.0 - 54.0
# ---- camera dietro, guscio stretto (si cambiano le tabelle della v1.2: questo modulo e la v1.2 non si usano insieme)
s12.ULN.update(y0=-24.0)
s12.HX.update(y0=9.0)
ULN, HX = s12.ULN, s12.HX
# ESP32-S3 SuperMini in piedi, parallelo al fianco destro (lontano dagli ULN2003 per il Wi-Fi), presa USB-C dietro
ESPV = dict(x0=-49.9, lungo=22.5, y0=16.8, sp=1.0, z0=58.0, alto=18.0)
s12.ESP.update(y0=ESPV["y0"], z=ESPV["z0"], largo=4.2)    # (per i cavi della v1.2 che arrivano all'ESP32)
ESP = s12.ESP

Y_DX13 = 26.45                 # come la v1.0
SPORGE = 2.0                   # la cornice della cassetta esce di 2 mm dal fianco
FACCIA = -1.0                  # faccia dello stepper, in |y| dalla parte della sua ruota (negativo = gia' dall'altra parte)
CORPO = 19.0                   # lunghezza del corpo dello stepper 28BYJ-48
PIASTRA = (FACCIA - 1.0, FACCIA - 4.0)   # piastra di supporto: dietro le alette, dalla parte del corpo
Z_DISP13 = 80.0                # display davanti, sotto le ruote

def gira180(m): return m.mirror([1, 0, 0]).mirror([0, 1, 0])


class Modello13(s12.Modello12):
    def __init__(self, chiave="2m"):
        super().__init__(chiave)
        self.nome = "Due ruote, stepper girati verso il centro (v1.3)"
        self.Y_DX = Y_DX13; self.Y_SX = -Y_DX13
        self.Y_MID = 0.0
        self.Z_DISP = (Z_DISP13, Z_DISP13 + OLED["alto"])
        self.X_CANALE = -47.5                                 # canale dei cavi piu' indietro: li' davanti c'e' una vite dello stepper

    @property
    def Z_TAGLIO(self): return 152                        # il cappello colorato comincia dove nella v1.2

    # ---------------- simmetria a mezzo giro: la geometria locale del lato destro e' quella del sinistro specchiata in X
    def metti(self, m, lato):
        if lato > 0: m = m.mirror([1, 0, 0])
        return super().metti(m, lato)

    def pignoni(self, phi=0.0):
        return [(m, (-cx if i == 1 else cx), cy, cz) for i, (m, cx, cy, cz) in enumerate(super().pignoni(phi))]

    def croci(self, phi=0.0, perno=True):
        return [(m, (-cx if i == 1 else cx), cy, cz) for i, (m, cx, cy, cz) in enumerate(super().croci(phi, perno))]

    def punto_fc(self, i, xp, yp, ay):
        x, y, z = super().punto_fc(i, xp, yp, ay)
        return (-x if i == 1 else x, y, z)

    def mondo(self, i, x, y, a):
        """Punto locale della ruota i (x, y = Z - Z_A, a = |Y| dalla sua parte) -> mondo."""
        s = -1 if i == 0 else 1
        return ((-x if i == 1 else x), s * a, self.Z_A + y)

    # ---------------- cassetta con la cornice
    def cassetta_locale(self):
        m = super().cassetta_locale()
        z0, z1 = self.Z_FL[1] - 0.01, self.Y_DX + SPORGE - self.Y0
        m += cil(self.R_CASS + 1.0, z0, z1) - cil(self.R_CASS - 0.8, z0 - 1, z1 + 1)          # anello
        m += cil(self.R_CASS + 1.0, z1 - 1.2, z1) - cil(self.R_AN_T + 0.2, z1 - 2, z1 + 1)      # bordo davanti (la ruota si vede dall'oblo')
        return m

    # ---------------- stepper girato: corpo dall'altra parte, albero verso la sua ruota
    def stepper_locale(self, i):
        cx, cy = self.pos_stepper(i); px, py = self.pos_pignone(i); zl = self.zl
        f = FACCIA
        m = cil(STEP["r"], zl(f - CORPO), zl(f), cx, cy)
        (e1x, e1y), (e2x, e2y) = self.alette_stepper(i)
        al = Manifold.batch_hull([cil(3.5, zl(f - 1.0), zl(f), e1x, e1y), cil(3.5, zl(f - 1.0), zl(f), e2x, e2y)])
        al -= cil(STEP["foro"] / 2, -40, 40, e1x, e1y) + cil(STEP["foro"] / 2, -40, 40, e2x, e2y)
        m += al
        m += ruota(scatola(10.0, 17.2, -7.3, 7.3, zl(f - CORPO + 0.5), zl(f - 1.0)), A_MOT).translate([cx, cy, 0])   # copricavi blu
        m += cil(STEP["boss"] / 2, zl(f) - 0.01, zl(f + STEP["h_boss"]), px, py)
        m += doppio_d(STEP["albero"] / 2, STEP["piatti"], zl(f + STEP["h_boss"]) - 0.01, zl(f + STEP["l_albero"]), px, py)
        return m

    def viti_motori(self):
        """M3 x 6 dalla parte dell'albero: testa bassa tra la faccia e il piano della croce, il gambo entra nella piastra."""
        m = Manifold(); zl = self.zl
        for i in range(2):
            v = Manifold()
            for ex, ey in self.alette_stepper(i):
                v += cil(1.25, zl(FACCIA - 6.0), zl(FACCIA), ex, ey) + cil(2.75, zl(FACCIA), zl(FACCIA + 1.6), ex, ey)
            m += self.metti(v, -1 if i == 0 else 1)
        return m

    def _piastra_locale(self, i):
        """Piastra dello stepper (parte del cappello) dietro le alette, con il buco per il corpo; braccio fino al tetto."""
        cx, cy = self.pos_stepper(i); zl = self.zl
        z0, z1 = zl(PIASTRA[1]), zl(PIASTRA[0])
        (e1x, e1y), (e2x, e2y) = self.alette_stepper(i)
        p = Manifold.batch_hull([cil(17.0, z0, z1, cx, cy), cil(4.0, z0, z1, e1x, e1y), cil(4.0, z0, z1, e2x, e2y)])
        p += scatola(cx - 6.0, cx + 6.0, cy, self.H - self.Z_A - 0.6, z0, z1)                  # braccio fino al tetto
        p += scatola(-self.X_HALF + 0.5, cx - 8.0, 45.5, 53.0, z0, z1)                          # braccio fino alla parete
        p -= cil(STEP["r"] + 0.4, z0 - 1, z1 + 1, cx, cy)
        p -= cil(self.R_CASS + 1.8, -40, 40)
        return p

    def _vuoti_piastra_locale(self, i):
        """Tutto quello che lo stepper attraversa: corpo, alette, copricavi, boss; fori delle viti nella piastra."""
        cx, cy = self.pos_stepper(i); px, py = self.pos_pignone(i); zl = self.zl
        v = cil(STEP["r"] + 0.4, zl(FACCIA - CORPO - 0.5), zl(FACCIA + 0.3), cx, cy)
        v += ruota(scatola(9.6, 17.6, -7.7, 7.7, zl(FACCIA - CORPO), zl(FACCIA + 0.3)), A_MOT).translate([cx, cy, 0])
        (e1x, e1y), (e2x, e2y) = self.alette_stepper(i)
        v += Manifold.batch_hull([cil(3.9, zl(FACCIA - 1.3), zl(FACCIA + 1.9), e1x, e1y), cil(3.9, zl(FACCIA - 1.3), zl(FACCIA + 1.9), e2x, e2y)])
        v += cil(STEP["boss"] / 2 + 0.6, zl(FACCIA), zl(FACCIA + STEP["l_albero"] + 0.5), px, py)
        v += scatola(cx - 30.0, cx + 30.0, cy - 30.0, cy + 30.0, zl(FACCIA) - 0.01, zl(FACCIA + 0.3))   # la faccia appoggia: niente parete centrale qui
        for ex, ey in self.alette_stepper(i): v += cil(1.3, zl(FACCIA - 6.5), zl(FACCIA), ex, ey)   # fori da 2,6 (la vite fa il filetto)
        return v

    # ---------------- ricarica dall'alto: ogni lato ha solo la sua meta' della canaletta; la sinistra e' girata dietro
    def _rot_sx(self, m, sd): return m.mirror([1, 0, 0]) if sd < 0 else m

    def fondo(self, sd, a=0.0): return self._rot_sx(super().fondo(sd, a), sd)
    def sportello_alto(self, s, theta=0.0): return self._rot_sx(super().sportello_alto(s, theta), s)

    def scivolo_alto(self, s):
        m = super().scivolo_alto(1) - scatola(20, 40, 0, 5.85, 170, 185)    # sponda interna a 5,85 dal centro: li' sotto gira la croce
        m = m if s > 0 else m.mirror([0, 1, 0])
        return self._rot_sx(m, s)

    def staffa_meta(self, sd):
        """Meta' della canaletta fissa (lato sd, ancora davanti come nella v1.2): pareti, testata interna, orecchie delle cerniere, appoggi."""
        x0, x1, w, hy, zb, zt, yp, zp, yi = RA["x0"], RA["x1"], RA["w"], RA["hy"], RA["zb"], RA["zt"], RA["yp"], RA["zp"], RA["yi"]
        ys = lambda a, b: sorted((sd * a, sd * b))
        zg = zb - s12.GIU_CANALETTA
        m = scatola(x0, x0 + w, *ys(yi - 0.8, hy), zg, zt) + scatola(x1 - w, x1, *ys(yi - 0.8, hy), zg, zt)   # pareti
        m += scatola(x0, x1, *ys(yi - 0.8, yi), zb, zt)                                                         # testata interna
        ya = ys(yp - 1.0, hy)
        m += scatola(x0, x0 + w, ya[0], ya[1], zp - 1.2, zb + 0.01) + scatola(x1 - w, x1, ya[0], ya[1], zp - 1.2, zb + 0.01)
        yf = ys(yi, yi + 1.0)
        m += scatola(x0, x0 + w + 0.6, yf[0], yf[1], zb + 1.01, zb + 1.4) + scatola(x1 - w - 0.6, x1, yf[0], yf[1], zb + 1.01, zb + 1.4)
        m -= cil_x(0.45, x0 - 1, x1 + 1, sd * yp, zp)
        m += scatola(x1 + 0.2, 46.0, *ys(16.5, 23.5), 208.5, 210.1)                                           # appoggi
        m += scatola(x1 + 0.2, x1 + 1.6, *ys(yi - 0.8, 23.5), 209.0, zt)                                        # piastra davanti
        for yc in (yi + 1.2, 20.0): m += scatola(x1 - 0.01, x1 + 0.21, *ys(yc - 2.0, yc + 2.0), 209.0, zt)
        return m

    def staffa_alta(self):
        return self.staffa_meta(1) + self.staffa_meta(-1).mirror([1, 0, 0])

    def vaschetta_alta(self, alfa=0.0):
        m = Manifold()
        for sd in (-1, 1):
            a = -alfa if alfa * sd < 0 else 0.0
            m += self.fondo(sd, a)
        return m

    # ---------------- display davanti, sotto le ruote; cicalino
    def display(self):
        x1 = self.X_HALF; h = OLED["largo"] / 2
        return scatola(x1 - PARETE - 0.2 - OLED["sp"], x1 - PARETE - 0.2, -h, h, self.Z_DISP[0], self.Z_DISP[1])

    # ---------------- ESP32 in piedi
    def _esp_zc(self): return ESPV["z0"] + ESPV["alto"] / 2
    def esp32(self):
        e = ESPV; x1 = e["x0"] + e["lungo"]; y0, y1 = e["y0"], e["y0"] + e["sp"]; z0, z1 = e["z0"], e["z0"] + e["alto"]; zc = self._esp_zc()
        m = scatola(e["x0"], x1, y0, y1, z0, z1) + scatola(e["x0"] + 3.0, x1 - 1.0, y1, y1 + 0.8, z0 + 1.0, z1 - 1.0)
        return m + scatola(e["x0"] - 0.4, e["x0"] + 7.4, y1, y1 + 3.2, zc - 4.5, zc + 4.5)          # presa USB-C

    def antenna(self):
        e = ESPV; x1 = e["x0"] + e["lungo"]
        return scatola(x1 - 4.0, x1, e["y0"], e["y0"] + e["sp"] + 0.8, e["z0"], e["z0"] + e["alto"])

    def spina_usb(self):
        yc = ESPV["y0"] + ESPV["sp"] + 1.6; zc = self._esp_zc()
        return scatola(-self.X_HALF - 17.0, -self.X_HALF - 0.3, yc - 3.5, yc + 3.5, zc - 5.5, zc + 5.5)

    def _guide_schede(self):
        """Costole con la scanalatura per gli ULN2003 e l'HX711 (contro la parete dietro); due mensole con la scanalatura per l'ESP32 in piedi."""
        xw = -self.X_HALF + PARETE - 0.01; xp = ULN["x_pcb"]; zf = self.Z_PIEDE + PARETE - 0.01
        m = Manifold(); v = Manifold()
        y0, y1 = ULN["y0"], ULN["y0"] + ULN["largo"]
        for ya, yb, sa, sb in ((self.Y_SX + PARETE - 0.01, y0 + 1.2, y0 - 0.2, y0 + 1.3), (y1 - 1.4, y1 + 1.2, y1 - 1.5, y1 + 0.2)):
            m += scatola(xw, xp + 2.8, ya, yb, zf, ULN["z"][1][1] + 0.2)
            v += scatola(xp - 0.2, xp + 1.8, sa, sb, ULN["z"][0][0] - 0.1, 200)
        h0, h1 = HX["y0"], HX["y0"] + HX["largo"]
        for ya, yb, sa, sb in ((h0 - 1.2, h0 + 0.8, h0 - 0.2, h0 + 0.9), (h1 - 0.8, h1 + 1.2, h1 - 0.9, h1 + 0.2)):
            m += scatola(xw, xp + 2.8, ya, yb, zf, HX["z0"] + HX["alto"] + 0.5)
            v += scatola(xp - 0.2, xp + 1.8, sa, sb, HX["z0"] - 0.1, 200)
        e = ESPV; xe = e["x0"] + e["lungo"] - 2.0
        for za, zb in ((e["z0"] - 2.0, e["z0"] + 0.6), (e["z0"] + e["alto"] - 0.6, e["z0"] + e["alto"] + 2.0)):
            m += scatola(xw, -40.0, e["y0"] - 1.6, self.Y_DX - PARETE + 0.01, za, zb)
        v += scatola(xw - 1, -39.0, e["y0"] - 0.2, e["y0"] + e["sp"] + 0.2, e["z0"] - 0.1, e["z0"] + e["alto"] + 0.1)   # scanalatura
        v += scatola(xw - 1, -39.0, e["y0"] + e["sp"] + 0.1, e["y0"] + e["sp"] + 1.2, e["z0"] + 0.6, e["z0"] + e["alto"] - 0.6)   # componenti
        return m - v

    def pezzi(self):
        P = super().pezzi()
        P.pop("17_staffa_alta", None)
        P["17_staffa_alta_sx"] = self.staffa_meta(-1).mirror([1, 0, 0])
        P["17_staffa_alta_dx"] = self.staffa_meta(1)
        return P

    # ---------------- guscio
    def corpo(self):
        if getattr(self, "_corpo", None) is not None: return self._corpo
        x0, x1, y0, y1 = -self.X_HALF, self.X_HALF, self.Y_SX, self.Y_DX
        m = v5.rett_arrotondato(x0, x1, y0, y1, R_SPIG, self.Z_PIEDE, self.H) ^ self._profilo(0)
        m -= v5.rett_arrotondato(x0 + PARETE, x1 - PARETE, y0 + PARETE, y1 - PARETE, R_SPIG - PARETE, self.Z_PIEDE + PARETE, self.H) ^ self._profilo(PARETE)
        m += self._zona_cappello() - scatola(-200, 200, -200, 200, self.Z_TAGLIO, 400)
        g1 = PARETE + 1.9
        m += (v5.rett_arrotondato(x0 + PARETE - 0.1, x1 - PARETE + 0.1, y0 + PARETE - 0.1, y1 - PARETE + 0.1, R_SPIG - PARETE, self.Z_TAGLIO, self.Z_TAGLIO + 1.6)
              - v5.rett_arrotondato(x0 + g1, x1 - g1, y0 + g1, y1 - g1, 1.0, self.Z_TAGLIO - 1, self.Z_TAGLIO + 2))
        z = self.Z_TAGLIO + 4.0
        while z + 1.0 < self.H - R_TOP:
            m -= (v5.rett_arrotondato(x0 - 1, x1 + 1, y0 - 1, y1 + 1, R_SPIG + 1, z, z + 1.0)
                  - v5.rett_arrotondato(x0 + 0.4, x1 - 0.4, y0 + 0.4, y1 - 0.4, R_SPIG - 0.4, z - 1, z + 2))
            z += 2.4
        # nicchia del bicchierino
        m -= scatola(self.CUP["x0"] - 0.6, x1 + 1, y0 - 1, y1 + 1, self.Z_PIEDE - 0.5, self.Z_NICCHIA)
        m += scatola(self.CUP["x0"] - 2.6, self.CUP["x0"] - 0.6, y0 + 0.01, y1 - 0.01, self.Z_PIEDE, self.Z_NICCHIA + 0.01)
        za = self.Z_CUP + self.CUP["alt"] + 6.0; xa = self.CUP["x0"] - 0.6; zn = self.Z_NICCHIA + 0.01
        sc = CrossSection([ccw([(xa - 0.01, za), (self.CUP["x0"] + 3.5, za), (self.CUP["x0"] + 3.5 + (zn - za), zn), (xa - 0.01, zn)])])
        m += Manifold.extrude(sc, 2 * self.CUP["y"]).translate([0, 0, -self.CUP["y"]]).transform([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0]])
        sq = CrossSection([ccw([(xa - 0.01, self.Z_NICCHIA + 0.01), (xa + 16.0, self.Z_NICCHIA + 0.01), (xa - 0.01, self.Z_NICCHIA - 16.0)])])
        for yy in (y0 + 0.01, y1 - 1.6 - 0.01):
            m += Manifold.extrude(sq, 1.6).translate([0, 0, yy]).transform([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0]])
        m += scatola(self.CUP["x0"] - 2.6, x1, y0 + 0.01, y1 - 0.01, self.Z_NICCHIA, self.Z_NICCHIA + PARETE) - scatola(self.PIATTO["x0"] - 3, self.PIATTO["x1"] + 3, -self.PIATTO["y"] - 2, self.PIATTO["y"] + 2, self.Z_NICCHIA - 1, self.Z_NICCHIA + 3)
        # sedi delle cassette e parete centrale
        for s in (-1, 1):
            m -= cil_y(self.R_CASS + 0.4, *sorted((s * 1.0, s * 40)), 0, self.Z_A)
            m -= cil_y(self.R_CASS + 1.4, *sorted((s * (self.Y0 + self.Z_FL[0] - 0.01), s * 40)), 0, self.Z_A)
        m += (scatola(-self.X_HALF + 1, self.X_HALF - 8.0, -0.95, 0.95, self.Z_IMB0 + 2.2, self.H - 1.0) ^ self._profilo(PARETE - 0.5)) - cil_y(6.0, -2, 2, 0, self.Z_A) \
             - scatola(self.X_TASTO - 10.5, self.X_TASTO + 10.5, -2, 2, self.H - PARETE - 11.5, self.H) \
             - scatola(self.X_TASTO - 13.6, self.X_TASTO + 13.6, -2, 2, self.H - PARETE - 2.0, self.H)
        culla = cil_y(self.R_CASS + 2.8, y0 + PARETE - 0.01, y1 - PARETE + 0.01, 0, self.Z_A) - cil_y(self.R_CASS + 1.4, y0, y1, 0, self.Z_A) - scatola(-100, 100, -100, 100, self.Z_A - 8, 400)
        culla -= scatola(-self.APRE - 3.6, self.APRE + 3.6, -100, 100, 0, self.Z_A)
        m += culla
        # appoggio della cella della dose, display, tasto
        cb = self.cella().bounding_box()
        m += scatola(cb[0], cb[0] + 15.0, cb[1], cb[4], self.Z_NICCHIA + PARETE - 0.01, cb[2])
        m -= scatola(x1 - PARETE - 1, x1 + 1, -11.5, 11.5, self.Z_DISP[0] + 8.0, self.Z_DISP[0] + 20.0)   # finestra dell'OLED 0,96"
        h = OLED["largo"] / 2 + 0.3; xd = x1 - PARETE - 0.2 - OLED["sp"]
        for zz in (self.Z_DISP[0] - 1.6, self.Z_DISP[1]):                                                 # due mensoline: il display ci si infila dall'interno
            m += scatola(xd - 1.0, x1 - PARETE + 0.01, -h, h, zz, zz + 1.6)
        m -= cil(self.R_TASTO + 0.4, self.H - 7, self.H + 1, self.X_TASTO, 0)
        # cicalino da 12 mm dietro la griglia davanti
        xa = x1 - PARETE
        m += cil_x(7.0, xa - 4.0, xa + 0.01, 0, Z_SUONO) - cil_x(6.15, xa - 5, xa + 1, 0, Z_SUONO)
        for dy, dz in [(0, 0)] + [(3.5 * math.cos(math.radians(a)), 3.5 * math.sin(math.radians(a))) for a in range(0, 360, 60)]:
            m -= cil_x(0.9, xa - 1, x1 + 1, dy, Z_SUONO + dz)
        # sensore di Hall del bicchierino
        m -= cil_x(2.4, self.CUP["x0"] - 3.1, self.CUP["x0"] - 1.2, 0, self.Z_CUP + 6.0)
        # ricarica dall'alto: per ogni lato il foro dello sportellino e l'appoggio della canaletta (la sinistra girata dietro)
        for sd in (-1, 1):
            f = scatola(RA["x0"] + 0.7, RA["x1"] - 0.7, *sorted((sd * (RA["yi"] - 0.3), sd * 24.5)), self.H - PARETE - 1.0, self.H + 1)
            a = scatola(37.9, 46.0, *sorted((sd * 16.5, sd * (self.Y_DX - PARETE + 0.01))), 196.5, 208.5)
            m -= self._rot_sx(f, sd); m += self._rot_sx(a, sd)
        m += scatola(cb[3] - 4.5, cb[3] - 0.5, cb[1] + 0.5, cb[4] - 0.5, self.Z_NICCHIA + PARETE - 0.01, cb[2] - G_FERMO)
        # piastre degli stepper, supporti dei finecorsa, blocchetti delle viti, colonnine del servo, guide delle schede
        for i, sd in ((0, -1), (1, 1)):
            m += self.metti(self._piastra_locale(i), sd)
            m += self.metti(self._supporto_fc_locale(i), sd)
            m += self.metti(self._blocchetto_locale(), sd)
        m += self._colonnine_servo()
        m += self._guide_schede()
        # canale dei cavi nella parete centrale (dietro) e passaggi
        m -= scatola(self.X_CANALE - 4, self.X_CANALE + 4, -0.5, 0.5, self.Z_IMB0, self.H - PARETE - 0.5)
        m -= scatola(self.X_CANALE - 4, self.X_CANALE + 4, -2, 2, self.Z_A + 38, self.H - PARETE - 0.5)
        for i, sd in ((0, -1), (1, 1)):
            m -= self.metti(self._vuoti_piastra_locale(i) + self._vuoti_fc_locale(i) + self._vuoti_vite_locale(), sd)
        # fori nella parete centrale per i cavi che passano da una parte all'altra (davanti in alto e sotto il tasto)
        m -= cil_y(1.4, -3, 3, 41.5, 212.5) + scatola(-10.4, -7.6, -3, 3, 200.6, 203.4)
        # presa USB-C dietro, all'altezza dell'ESP32
        yc = ESPV["y0"] + ESPV["sp"] + 1.6; zc = self._esp_zc()
        m -= scatola(-self.X_HALF - 1, -self.X_HALF + PARETE + 1, yc - 2.1, yc + 2.1, zc - 4.8, zc + 4.8)
        self._corpo = m
        return m

    # ---------------- cavi
    def cavi(self):
        """I cavi di davanti (stepper e finecorsa della ruota destra) vanno dietro sotto il tetto: a destra del centro davanti,
        passano sotto il tasto, attraversano la parete centrale e arrivano al canale dietro dalla parte sinistra."""
        L = [c for c in super().cavi() if not c[0].startswith(("stepper ", "display", "tasto", "finecorsa destro", "nastro - ESP32", "HX711 - ESP32"))]
        ze = ESPV["z0"]; ye = ESPV["y0"] + ESPV["sp"] + 0.6
        L.append(("nastro - ESP32 (display, tasto, finecorsa)", "#2f6fd0", 0.8, [(self.X_CANALE + 1.0, 0.5, Z_NASTRO + 1.6), (-34.0, 10.0, 82.2), (-33.0, ye + 1.0, 72.0)], ["esp32"]))
        L.append(("HX711 - ESP32", "#16a085", 0.8, [(-46.0, 20.0, HX["z0"] + HX["alto"] - 0.5), (-45.5, 20.0, 50.0), (-37.0, 20.5, 54.5), (-35.0, ye + 1.0, ze + 1.5)], ["hx711", "esp32"]))
        xc = self.X_CANALE; zr = 202.0; zc = self.Z_A + 64.0
        verso_dietro = [(14.0, 2.5, zr), (-9.0, 2.5, zr), (-9.0, -2.2, zr), (xc + 1.0, -2.2, zr), (xc + 0.3, -0.9, zr - 1.0), (xc, -0.9, zc)]
        cx, cy = self.pos_stepper(0); a = math.radians(A_MOT)
        ux, uy = cx + 16.2 * math.cos(a), cy + 16.2 * math.sin(a)
        p0 = self.mondo(0, ux, uy, FACCIA - 10.0)
        L.append(("stepper sinistro", "#c0392b", 0.9, [p0, (-41.5, p0[1], 212.5), (-41.5, 2.0, 212.5), (xc + 0.3, 0.9, 205.0), (xc, 0.9, zc)], ["motore_1"]))
        p0 = self.mondo(1, ux, uy, FACCIA - 10.0)
        L.append(("stepper destro", "#c0392b", 0.9, [p0, (41.5, p0[1], 212.5), (41.5, 2.5, 212.5), (16.0, 2.5, 212.5)] + verso_dietro, ["motore_2"]))
        p0 = self.punto_fc(1, FC["punta"] + FC["stelo"] + FC["corpo"] + 0.35, -1.0, FC["yc"])
        p1 = self.punto_fc(1, FC["punta"] + FC["stelo"] + FC["corpo"] + 0.35, -6.9, FC["yc"])
        L.append(("finecorsa destro", "#e0b400", 0.7, [p0, p1, (p1[0], p1[1], p1[2] + 1.6), (44.6, 2.5, p1[2] + 3.0), (44.6, 2.5, zr), (16.0, 2.5, zr)] + verso_dietro, ["finecorsa_dx"]))
        hr = self.H - PARETE
        L.append(("tasto", "#e0b400", 0.8, [(-10.4, 6.0, hr - 10.7), (-9.0, 6.0, zr), (-9.0, -2.2, zr)] + verso_dietro[3:], ["interruttore"]))
        zd = self.Z_DISP[0]
        L.append(("display", "#2f6fd0", 0.8, [(46.4, 0.0, zd + 3.0), (45.0, 3.0, zd + 3.0), (43.0, 12.0, 70.0), (40.0, 20.5, 60.0), (-27.0, 20.5, 60.0), (-30.0, ESPV["y0"] + ESPV["sp"] + 1.4, 63.0)], ["display", "esp32"]))
        return L


Modello = Modello13

def genera(chiave, cartella):
    M = Modello13(chiave); P = M.pezzi(); C = M.componenti()
    for d in ("stampa", "assieme", "componenti"):
        dd = os.path.join(cartella, d); os.makedirs(dd, exist_ok=True)
        for f in os.listdir(dd): os.remove(os.path.join(dd, f))
    def su_piano(mesh, nome):
        verso, area, st = stampa(mesh); b = st.bounds; st.apply_translation([-(b[0][0] + b[1][0]) / 2, -(b[0][1] + b[1][1]) / 2, 0])
        st.export(os.path.join(cartella, "stampa", nome + ".stl"))
    for n, m in P.items():
        mesh = a_mesh(m); mesh.export(os.path.join(cartella, "assieme", n + ".stl")); su_piano(mesh, n)
    for n, m in C.items(): a_mesh(m).export(os.path.join(cartella, "componenti", n + ".stl"))
    for i, lato in enumerate(("sx", "dx")):
        su_piano(a_mesh(M.croci(perno=False)[i][0]), "14_croce_" + lato)
        su_piano(a_mesh(M.pignoni()[i][0]), "15_pignone_" + lato)
    return M, P, C

if __name__ == "__main__":
    import zipfile
    qui = os.path.dirname(os.path.abspath(__file__)); out = os.path.join(qui, "..", "v13")
    M, P, C = genera("2m", os.path.join(out, "stl"))
    x, y, z = M.misure()
    print(f"== {M.nome}: corpo {x:.1f} x {y:.1f} x {z:.1f} mm = {x * y * z / 1e6:.2f} litri; piede {M.PIEDE['x1'] - M.PIEDE['x0']:.0f} x {2 * M.PIEDE['y']:.0f}")
    for n, m in P.items(): print(f"   {n:22s} pezzi {len(m.decompose())}  {m.volume() / 1000:6.1f} cm3")
    st = os.path.join(out, "stl", "stampa")
    with zipfile.ZipFile(os.path.join(out, "blistra_v13_stampa.zip"), "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(os.listdir(st)): z.write(os.path.join(st, f), os.path.join("blistra_v13_stampa", f))
    print("zip:", os.path.join(out, "blistra_v13_stampa.zip"))
