"""Demo data for the seed command."""
from .models import Production

DEMO_TITLE = "The Lighthouse Keeper (demo)"

DEMO_SCRIPT = """\
THE LIGHTHOUSE KEEPER
A short play in two scenes.

SCENE 1. The lamp room at the top of the lighthouse. Night. A storm outside.

(Thunder. The great lamp turns slowly. MARA, the keeper, trims the wick with a pair of brass scissors.)

MARA: Forty years I've kept this light, and never a night like this.

(A knock at the trapdoor. TOM, a young fisherman, climbs up, soaked, holding a lantern.)

TOM: Mrs. Hale! The Gull's lost her mast off the north rocks. My father's aboard.
MARA: Then the lamp stays lit, whatever the storm does to us. Fetch the foghorn.
TOM: It's rusted through.
MARA: Then we ring the bell.

(MARA pulls the bell rope. The bell rings out over the wind. Lights flicker.)

SCENE 2. The rocky shore below the lighthouse. Dawn.

(The storm has passed. Birdsong and gentle waves. TOM drags a wooden oar onto the shore. CAPTAIN HALE, his father, limps behind him with a torn sail around his shoulders.)

CAPTAIN HALE: We saw the light, and then we heard the bell.
TOM: She rang it all night.

(MARA comes down the path carrying a kettle and three tin cups.)

MARA: Tea first. Then you can tell me how you lost a perfectly good mast.

(They laugh. The sun rises. Lights fade.)

END
"""


def create_demo_data(user):
    """Give the user a demo production. Safe to rerun: leaves an existing copy alone."""
    production, created = Production.objects.get_or_create(
        owner=user, title=DEMO_TITLE, defaults={"script": DEMO_SCRIPT},
    )
    return created
