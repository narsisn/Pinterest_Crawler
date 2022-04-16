"""
Word count topology
"""

from streamparse import Grouping, Topology

from bolts.Pinterest_visualSearchParserBolt import Pinterest_visualSearchParserBolt
from spouts.Pinterest_VisualSearchSpout import Pinterest_VisualSearchSpout


class Pinterest_VisualSearchTopology(Topology):
    word_spout = Pinterest_VisualSearchSpout.spec()
    count_bolt = Pinterest_visualSearchParserBolt.spec(inputs=word_spout, par=2  )
