from django.db import migrations, models
import ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('c2', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='c2techactivities',
            name='remarks',
            field=ckeditor.fields.RichTextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='c2techactivities',
            name='remark_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.deletion.SET_NULL, related_name='tech_remarks', to='c2.c2user'),
        ),
    ] 