# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2012 Nebula, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages

from openstack_dashboard import api


class CreateSnapshot(forms.SelfHandlingForm):
    instance_name = forms.CharField(label=_("Instance Name"),
                                    required=False,
                                    widget=forms.TextInput(
                                        attrs={'readonly': 'readonly'}))
    instance_id = forms.CharField(label=_("Instance ID"),
                                  widget=forms.HiddenInput(),
                                  required=False)
    name = forms.CharField(max_length="255", label=_("Snapshot Name"))

    def __init__(self, request, *args, **kwargs):
        super(CreateSnapshot, self).__init__(request, *args, **kwargs)

        # populate instance_id and instance_name
        instance_id = kwargs.get('initial', {}).get('instance_id')
        instance = api.nova.server_get(request, instance_id)
        self.fields['instance_name'].initial = instance.name

    def handle(self, request, data):
        try:
            snapshot = api.nova.snapshot_create(request,
                                                data['instance_id'],
                                                data['name'])
            vals = {"name": data['name'], "inst": data['instance_name']}
            messages.success(request, _('Snapshot "%(name)s" created for '
                                        'instance "%(inst)s"') % vals)
            return snapshot
        except Exception:
            redirect = reverse("horizon:project:instances:index")
            exceptions.handle(request,
                              _('Unable to create snapshot.'),
                              redirect=redirect)
