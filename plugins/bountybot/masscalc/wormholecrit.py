"""
Created on 2016-01-22

@author: Valtyr Farshield
"""


class WormholeCrit:
    """
    Wormhole Mass Calculator
    """

    NEW = 4
    STABLE = 3
    DESTAB = 2
    CRIT = 1
    COLLAPSED = 0

    def __init__(self, wh_mass, wh_max_jump, wh_state):
        self.n_mass = 0
        self.max_jump = 0
        self.mass = (0, 0)
        self.kstate = False
        self.wh_state = WormholeCrit.COLLAPSED

        self._mf = (0, 0)
        self._ms = (0, 0)
        self._md = (0, 0)
        self._mc = (0, 0)
        self._last_mass = 0

        self.change_type(wh_mass, wh_max_jump, wh_state)

    def __str__(self):
        if self.wh_state == WormholeCrit.NEW:
            state = "new"
        elif self.wh_state == WormholeCrit.STABLE:
            state = "stable"
        elif self.wh_state == WormholeCrit.DESTAB:
            state = "unstable"
        elif self.wh_state == WormholeCrit.CRIT:
            state = "critical"
        elif self.wh_state == WormholeCrit.COLLAPSED:
            state = "collapsed"
        else:
            state = "unknown"

        return "Mass is between `{} kT` and `{} kT`, Maxjump: `{} kT`, Status: `{}`".format(
            self.mass[0],
            self.mass[1],
            self.max_jump,
            state
        )

    def change_type(self, wh_mass, wh_max_jump, wh_state):
        self.n_mass = wh_mass
        self.max_jump = wh_max_jump

        self._mf = (0.9*self.n_mass, 1.1*self.n_mass)
        self._ms = (0.45*self.n_mass, 1.1*self.n_mass)
        self._md = (0.09*self.n_mass, 0.55*self.n_mass)
        self._mc = (0, 0.11*self.n_mass)

        self.wh_state = wh_state
        if wh_state == WormholeCrit.NEW:
            self.mass = self._mf
            self.kstate = True
        elif wh_state == WormholeCrit.STABLE:
            self.mass = self._ms
            self.kstate = False
        elif wh_state == WormholeCrit.DESTAB:
            self.mass = self._md
            self.kstate = False
        elif wh_state == WormholeCrit.CRIT:
            self.mass = self._mc
            self.kstate = False
        else:
            pass

    def splash(self, ship_mass):
        wormhole_shrunk = False
        succesful_splash = 0 < ship_mass <= self.max_jump

        if succesful_splash:
            self._last_mass = self.mass[0] - ship_mass
            if self._last_mass < 0:
                self._last_mass = 0
            self.mass = (self.mass[0], self.mass[1] - ship_mass)

            # compute lower limit if necessary
            if self.kstate:

                # New or stable wormhole
                if self.wh_state == WormholeCrit.NEW or self.wh_state == WormholeCrit.STABLE:
                    if self._last_mass < self._ms[0]:
                        self.mass = (self._ms[0], self.mass[1])
                        self.kstate = False
                    else:
                        self.mass = (self._last_mass, self.mass[1])

                # Destable wormhole
                elif self.wh_state == WormholeCrit.DESTAB:
                    if self._last_mass < self._md[0]:
                        self.mass = (self._md[0], self.mass[1])
                        self.kstate = False
                    else:
                        self.mass = (self._last_mass, self.mass[1])

                # Critical mass wormhole
                elif self.wh_state == WormholeCrit.CRIT:
                    if self._last_mass < self._mc[0]:
                        self.mass = (self._mc[0], self.mass[1])
                        self.kstate = False
                    else:
                        self.mass = (self._last_mass, self.mass[1])

                # Collapsed wormhole
                else:
                    pass

            # auto-shrink ?
            while self.mass[1] < self.mass[0] or \
                    (self.wh_state in [WormholeCrit.NEW, WormholeCrit.STABLE] and self.mass[1] < self._ms[0]) or \
                    (self.wh_state == WormholeCrit.DESTAB and self.mass[1] < self._md[0]) or \
                    (self.wh_state == WormholeCrit.CRIT and self.mass[1] < self._mc[0]):
                wormhole_shrunk = True
                self.shrink()

        return [succesful_splash, wormhole_shrunk]

    def shrink(self):
        succesful_shrink = True

        # New or stable wormhole
        if self.wh_state == WormholeCrit.NEW or self.wh_state == WormholeCrit.STABLE:
            if self.mass[0] <= self._md[1]:
                self.wh_state = WormholeCrit.DESTAB
                self.kstate = True
                self.mass = (
                    self._last_mass,
                    self._md[1] if self._md[1] < self.mass[1] else self.mass[1]
                )
            else:
                succesful_shrink = False

        # Destable wormhole
        elif self.wh_state == WormholeCrit.DESTAB:
            if self.mass[0] <= self._mc[1]:
                self.wh_state = WormholeCrit.CRIT
                self.kstate = True
                self.mass = (
                    self._last_mass,
                    self._mc[1] if self._mc[1] < self.mass[1] else self.mass[1]
                )
            else:
                succesful_shrink = False

        # Critical mass wormhole
        elif self.wh_state == WormholeCrit.CRIT:
            if self.mass[0] <= self._mc[1]:
                self.wh_state = WormholeCrit.COLLAPSED
                self.kstate = True
                self.mass = (0, 0)
            else:
                succesful_shrink = False

        # Collapsed wormhole
        else:
            pass

        return succesful_shrink

    def collapse_chance(self, ship_mass):
        plausible = 0 < ship_mass <= self.max_jump
        if plausible:
            chance = float(ship_mass - self.mass[0]) / (self.mass[1] - self.mass[0]) * 100.0

            if chance < 0:
                chance = 0
            if chance > 100:
                chance = 100
        else:
            chance = 0

        return [plausible, chance]


def main():
    wh_mass = float(input("Wormhole mass [e.g. 2000]="))
    wh_max_jump = float(input("Wormhole max jump [e.g. 300]="))
    state = int(input("Wormhole state [4 - Fresh, 3 - Stable, 2 - Destab, 1 - Crit]="))

    w = WormholeCrit(wh_mass, wh_max_jump, state)
    print(w)
    print("")
    print("Commands:")
    print("  -1: quit")
    print("   0: shrink wormhole")
    print("<nr>: splash <nr> mass, e.g. 300")

    while True:
        user_input = float(input("Command: "))

        if user_input == -1:
            break
        elif user_input == 0:
            succesful_shrink = w.shrink()
            if succesful_shrink:
                print("Successful shrink. {}".format(w))
            else:
                print("Unable to shrink. {}".format(w))
        elif user_input > 0:
            [splash_ok, state_changed] = w.splash(user_input)
            if not splash_ok:
                print("Ship is too heavy!")
            if state_changed:
                print("Wormhole shrunk!")
            print(w)
        else:
            print("Invalid command")


if __name__ == "__main__":
    main()
