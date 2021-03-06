# Generated by Django 3.2.5 on 2021-10-21 13:15

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Agent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='agent')),
                ('currentYear', models.BooleanField(default=True, verbose_name='Année courante')),
            ],
            options={
                'verbose_name': 'Secteur',
            },
        ),
        migrations.CreateModel(
            name='AgentFinitions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='agent_finitions')),
                ('ratioTargetedVisit', models.FloatField(default=0.3, verbose_name='Ratio des visites ciblées')),
                ('TargetedNbVisit', models.IntegerField(default=800, verbose_name='Ratio des visites ciblées')),
                ('currentYear', models.BooleanField(default=True, verbose_name='Année courante')),
            ],
            options={
                'verbose_name': 'Agent Finitions',
            },
        ),
        migrations.CreateModel(
            name='Bassin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='bassin')),
                ('currentYear', models.BooleanField(default=True, verbose_name='Année courante')),
            ],
            options={
                'verbose_name': 'Bassin',
            },
        ),
        migrations.CreateModel(
            name='Dashboard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default=None, max_length=64)),
                ('geoOrTrade', models.CharField(default='geo', max_length=6)),
                ('comment', models.CharField(default=None, max_length=2048)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Dep',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=2, verbose_name='dep')),
                ('currentYear', models.BooleanField(default=True, verbose_name='Année courante')),
            ],
            options={
                'verbose_name': 'Département',
            },
        ),
        migrations.CreateModel(
            name='Drv',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=16, verbose_name='drv')),
                ('currentYear', models.BooleanField(default=True, verbose_name='Année courante')),
            ],
            options={
                'verbose_name': 'DRV',
            },
        ),
        migrations.CreateModel(
            name='Enseigne',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Inconnu', max_length=64, verbose_name='name')),
                ('currentYear', models.BooleanField(default=True, verbose_name='Année courante')),
            ],
            options={
                'verbose_name': 'Enseigne',
            },
        ),
        migrations.CreateModel(
            name='Ensemble',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Inconnu', max_length=64, verbose_name='name')),
                ('currentYear', models.BooleanField(default=True, verbose_name='Année courante')),
            ],
            options={
                'verbose_name': 'Ensemble',
            },
        ),
        migrations.CreateModel(
            name='Industry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Inconnu', max_length=32, unique=True, verbose_name='name')),
            ],
            options={
                'verbose_name': 'Industrie',
            },
        ),
        migrations.CreateModel(
            name='LabelForGraph',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('axisType', models.CharField(default=None, max_length=32)),
                ('label', models.CharField(default=None, max_length=32)),
                ('color', models.CharField(default=None, max_length=32)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Layout',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default=None, max_length=64, unique=True)),
                ('template', models.CharField(default=None, max_length=2048)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ParamVisio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field', models.CharField(max_length=64, unique=True)),
                ('prettyPrint', models.CharField(default=None, max_length=64)),
                ('fvalue', models.CharField(max_length=64)),
                ('typeValue', models.CharField(max_length=64)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Pdv',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(default='Inconnu', max_length=10, verbose_name='PDV code')),
                ('name', models.CharField(default='Inconnu', max_length=64, verbose_name='PDV')),
                ('latitude', models.FloatField(default=0.0, verbose_name='Latitude')),
                ('longitude', models.FloatField(default=0.0, verbose_name='Longitude')),
                ('available', models.BooleanField(default=True)),
                ('sale', models.BooleanField(default=True, verbose_name='Ne vend pas de plaque')),
                ('redistributed', models.BooleanField(default=True, verbose_name='Redistribué')),
                ('redistributedFinitions', models.BooleanField(default=True, verbose_name='redistribué Enduit')),
                ('pointFeu', models.BooleanField(default=False, verbose_name='Point Feu')),
                ('onlySiniat', models.BooleanField(default=False, verbose_name='100% Siniat')),
                ('closedAt', models.DateTimeField(blank=True, default=None, null=True, verbose_name='Date de Fermeture')),
                ('currentYear', models.BooleanField(default=True, verbose_name='Année courante')),
                ('agent', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='visioServer.agent', verbose_name='Secteur')),
                ('agentFinitions', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='visioServer.agentfinitions', verbose_name='Secteur Finition')),
                ('bassin', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='visioServer.bassin', verbose_name='Bassin')),
                ('dep', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='visioServer.dep', verbose_name='Département')),
                ('drv', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='visioServer.drv', verbose_name='Région')),
                ('enseigne', models.ForeignKey(default=7, on_delete=django.db.models.deletion.PROTECT, to='visioServer.enseigne', verbose_name='Enseigne')),
                ('ensemble', models.ForeignKey(default=43, on_delete=django.db.models.deletion.PROTECT, to='visioServer.ensemble', verbose_name='Ensemble')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Inconnu', max_length=32, unique=True, verbose_name='name')),
            ],
            options={
                'verbose_name': 'Produit',
            },
        ),
        migrations.CreateModel(
            name='SegmentCommercial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=16, verbose_name='segment_commercial')),
                ('currentYear', models.BooleanField(default=True, verbose_name='Année courante')),
            ],
            options={
                'verbose_name': 'Segment Commercial',
            },
        ),
        migrations.CreateModel(
            name='SegmentMarketing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, verbose_name='segment_marketing')),
                ('currentYear', models.BooleanField(default=True, verbose_name='Année courante')),
            ],
            options={
                'verbose_name': 'Segment Marketing',
            },
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Inconnu', max_length=64, verbose_name='name')),
                ('currentYear', models.BooleanField(default=True, verbose_name='Année courante')),
            ],
            options={
                'verbose_name': 'Site',
            },
        ),
        migrations.CreateModel(
            name='SousEnsemble',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Inconnu', max_length=64, verbose_name='name')),
                ('currentYear', models.BooleanField(default=True, verbose_name='Année courante')),
            ],
            options={
                'verbose_name': 'Sous-Ensemble',
            },
        ),
        migrations.CreateModel(
            name='Ville',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True, verbose_name='ville')),
            ],
            options={
                'verbose_name': 'Ville',
            },
        ),
        migrations.CreateModel(
            name='Widget',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default=None, max_length=32, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='WidgetCompute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('axis1', models.CharField(default=None, max_length=32, verbose_name='Axe 1')),
                ('axis2', models.CharField(default=None, max_length=32, verbose_name='Axe 2')),
                ('indicator', models.CharField(default=None, max_length=32, verbose_name='Indicateur')),
                ('groupAxis1', models.CharField(default=None, max_length=4096, verbose_name='Filtre Axe 1')),
                ('groupAxis2', models.CharField(default=None, max_length=4096, verbose_name='Filtre Axe 2')),
                ('percent', models.CharField(default='no', max_length=32, verbose_name='Pourcentage')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='WidgetParams',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default=None, max_length=128)),
                ('subTitle', models.CharField(default=None, max_length=2048)),
                ('position', models.CharField(default=None, max_length=1)),
                ('unity', models.CharField(default=None, max_length=32, verbose_name='Unité')),
                ('widget', models.ForeignKey(default=None, on_delete=django.db.models.deletion.DO_NOTHING, to='visioServer.widget')),
                ('widgetCompute', models.ForeignKey(default=None, on_delete=django.db.models.deletion.DO_NOTHING, to='visioServer.widgetcompute')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Visit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=datetime.date.today, verbose_name='Mois des visites')),
                ('nbVisit', models.IntegerField(default=1, verbose_name='Nombre de visites')),
                ('pdv', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='visioServer.pdv')),
            ],
            options={
                'verbose_name': 'Visites Mensuels',
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('idGeo', models.IntegerField(blank=True, default=None)),
                ('lastUpdate', models.DateTimeField(blank=True, default=None, null=True, verbose_name='Dernière mise à jour')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TreeNavigation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('geoOrTrade', models.CharField(default='Geo', max_length=6)),
                ('levelName', models.CharField(default=None, max_length=32)),
                ('prettyPrint', models.CharField(default=None, max_length=32)),
                ('listDashboards', models.ManyToManyField(default=None, to='visioServer.Dashboard')),
                ('subLevel', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='visioServer.treenavigation')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TargetLevel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(blank=True, default=None, null=True, verbose_name='Date de Saisie')),
                ('vol', models.FloatField(default=0.0, verbose_name='Cible visée en Volume P2CD')),
                ('dn', models.IntegerField(default=0, verbose_name='Cible visée en dn P2CD')),
                ('currentYear', models.BooleanField(default=True, verbose_name='Année courante')),
                ('agent', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='visioServer.agent')),
                ('agentFinitions', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='visioServer.agentfinitions')),
                ('drv', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='visioServer.drv')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Target',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(blank=True, default=None, null=True, verbose_name='Date de Saisie')),
                ('redistributed', models.BooleanField(default=True, verbose_name='Redistribué')),
                ('redistributedFinitions', models.BooleanField(default=True, verbose_name='Redistribué Enduit')),
                ('sale', models.BooleanField(default=True, verbose_name='Ne vend pas de plaque')),
                ('targetP2CD', models.FloatField(blank=True, default=0.0, verbose_name='Cible P2CD')),
                ('targetFinitions', models.BooleanField(default=False, verbose_name='Cible Finitions')),
                ('greenLight', models.CharField(blank=True, choices=[('g', 'vert'), ('o', 'orange'), ('r', 'rouge')], default=None, max_length=1, verbose_name='Feu Ciblage P2CD')),
                ('commentTargetP2CD', models.TextField(blank=True, default=None, verbose_name='Commentaires ciblage P2CD')),
                ('bassin', models.CharField(blank=True, default='', max_length=64)),
                ('pdv', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='visioServer.pdv')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='pdv',
            name='segmentCommercial',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='visioServer.segmentcommercial'),
        ),
        migrations.AddField(
            model_name='pdv',
            name='segmentMarketing',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='visioServer.segmentmarketing'),
        ),
        migrations.AddField(
            model_name='pdv',
            name='site',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='visioServer.site'),
        ),
        migrations.AddField(
            model_name='pdv',
            name='sousEnsemble',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='visioServer.sousensemble', verbose_name='Sous-Ensemble'),
        ),
        migrations.AddField(
            model_name='pdv',
            name='ville',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='visioServer.ville'),
        ),
        migrations.CreateModel(
            name='LogUpdate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(blank=True, default=None, null=True, verbose_name='Date de Reception')),
                ('data', models.TextField(blank=True, default='', verbose_name='Json des updates reçus')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='LogClient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(blank=True, default=None, null=True, verbose_name='Date de Reception')),
                ('view', models.BooleanField(default=False, verbose_name='Geo ou Enseigne')),
                ('year', models.BooleanField(default=False, verbose_name='Année selectionnée')),
                ('path', models.CharField(default=None, max_length=64, verbose_name='Navigation')),
                ('mapVisible', models.BooleanField(default=False, verbose_name='Tableau de bord ou cartographie')),
                ('mapFilters', models.CharField(default=None, max_length=1024, verbose_name='CategorieSelectionnée')),
                ('stayConnected', models.BooleanField(default=False, verbose_name='Resté connecté')),
                ('dashboard', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='visioServer.dashboard')),
                ('pdv', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='visioServer.pdv')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
                ('widgetParams', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='visioServer.widgetparams')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='dashboard',
            name='layout',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='visioServer.layout'),
        ),
        migrations.AddField(
            model_name='dashboard',
            name='widgetParams',
            field=models.ManyToManyField(to='visioServer.WidgetParams'),
        ),
        migrations.CreateModel(
            name='AxisForGraph',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default=None, max_length=32)),
                ('labels', models.ManyToManyField(to='visioServer.LabelForGraph')),
            ],
            options={
                'verbose_name': 'Axes pour les graphiques',
            },
        ),
        migrations.AddField(
            model_name='agentfinitions',
            name='drv',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.DO_NOTHING, to='visioServer.drv'),
        ),
        migrations.CreateModel(
            name='Sales',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(blank=True, default=None, null=True, verbose_name='Date de Saisie')),
                ('volume', models.FloatField(blank=True, default=0.0, verbose_name='Volume')),
                ('currentYear', models.BooleanField(default=True, verbose_name='Année courante')),
                ('industry', models.ForeignKey(default=17, on_delete=django.db.models.deletion.CASCADE, to='visioServer.industry')),
                ('pdv', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='visioServer.pdv')),
                ('product', models.ForeignKey(default=6, on_delete=django.db.models.deletion.CASCADE, to='visioServer.product')),
            ],
            options={
                'verbose_name': 'Ventes',
                'unique_together': {('pdv', 'industry', 'product')},
            },
        ),
    ]
