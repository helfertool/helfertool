![Helfertool](https://raw.githubusercontent.com/helfertool/graphics/master/logo/logo_with_text.png)

Helfertool is a Python3 and Django based tool that allows to manage the
volunteers or staff for an event. See <https://www.helfertool.org> for more information.

We have a Matrix room now to discuss development and administration of the Helfertool: [#helfertool:matrix.org](https://matrix.to/#/#helfertool:matrix.org)

[![Matrix](https://www.helfertool.org/img/matrix-badge-github.svg)](https://matrix.to/#/#helfertool:matrix.org)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=helfertool_helfertool&metric=alert_status)](https://sonarcloud.io/dashboard?id=helfertool_helfertool)

# Install

Please have a look at the
[admin guide](https://docs.helfertool.org/admin/index.html)
in our documentation.

# Docker Compose
For a immediate testing a docker compose file is available
```bash
# Allow bind to container
chmod -R o+rw test/container
docker-compose up -d
sleep 10
docker-compose exec helfertool helfertool init
docker-compose exec helfertool helfertool manage createsuperuser
# import example event
docker-compose exec helfertool helfertool manage exampledata 
```

# Environment for development

Please have a look at the
[development guide](https://docs.helfertool.org/development/environment.html)
in our documentation.

# Issues

Please feel free to create issues here in Github!

# License

Copyright (C) 2015-2025  Sven Hertle and contributors

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
