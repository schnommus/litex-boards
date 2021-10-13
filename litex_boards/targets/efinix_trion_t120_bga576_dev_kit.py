#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Franck Jullien <franck.jullien@collshade.fr>
# Copyright (c) 2021 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

import argparse

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex_boards.platforms import efinix_trion_t120_bga576_dev_kit

from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform):
        self.clock_domains.cd_sys = ClockDomain()

        # # #

        clk40 = platform.request("clk40")
        rst_n = platform.request("user_btn", 0)

        self.comb += self.cd_sys.clk.eq(clk40)
        self.specials += AsyncResetSynchronizer(self.cd_sys, ~rst_n)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(40e6), with_led_chaser=True, **kwargs):
        platform = efinix_trion_t120_bga576_dev_kit.Platform()

        # SoCCore ----------------------------------------------------------------------------------
        kwargs["integrated_rom_no_we"]  = True # FIXME: Avoid this.
        kwargs["integrated_sram_no_we"] = True # FIXME: Avoid this.
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident          = "LiteX SoC on Efinix Trion T120 BGA576 Dev Kit",
            ident_version  = True,
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on Basys3")
    parser.add_argument("--build", action="store_true", help="Build bitstream")
    parser.add_argument("--load",  action="store_true", help="Load bitstream")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    soc     = BaseSoC(**soc_core_argdict(args))
    builder = Builder(soc, **builder_argdict(args))
    builder.build(run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, f"outflow/{soc.build_name}.bit"))

if __name__ == "__main__":
    main()