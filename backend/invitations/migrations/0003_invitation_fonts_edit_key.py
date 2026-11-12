import secrets

from django.db import migrations, models

from invitations.models import generate_edit_key


def fill_edit_keys(apps, schema_editor):
    Invitation = apps.get_model("invitations", "Invitation")
    for invitation in Invitation.objects.all().only("pk"):
        invitation.edit_key = secrets.token_urlsafe(24)
        invitation.save(update_fields=["edit_key"])


class Migration(migrations.Migration):

    dependencies = [
        ("invitations", "0002_invitation_category"),
    ]

    operations = [
        migrations.AddField(
            model_name="invitation",
            name="fonts",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="invitation",
            name="edit_key",
            field=models.CharField(blank=True, max_length=43, null=True),
        ),
        migrations.RunPython(fill_edit_keys, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="invitation",
            name="edit_key",
            field=models.CharField(
                default=generate_edit_key,
                editable=False,
                max_length=43,
                unique=True,
            ),
        ),
    ]
