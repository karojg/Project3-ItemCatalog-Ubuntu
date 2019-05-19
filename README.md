# Item Catalog Project
"The Item Catalog project consists of developing an application that provides a list of items within a variety of categories, as well as provide a user registration and authentication system."

## Project Structure
```
.
├── application.py
├── client_secrets.json
├── catalogdb_setup.py
├── fakedb.py
├── catalog.db
├── README.md
├── static
│   └── style.css
└── templates
    ├── categories.html
    ├── categoryItems.html
    ├── deleteCategoryItem.html
    ├── editCategoryItem.html
    ├── header.html
    ├── itemDescription.html
    ├── login.html
    └── newCategoryItem.html
```

## Instructions

1. Download and install [Vagrant](https://www.vagrantup.com/downloads.html).

2. Download and install [VirtualBox](https://www.virtualbox.org/wiki/Downloads).

3. Clone or download the Vagrant VM configuration file from [here](https://github.com/udacity/fullstack-nanodegree-vm).
    - You will end up with a new directory containing the VM files.
    - Change directory to the vagrant directory:

        ```bash
        cd vagrant/
        ```

5. In `vagrant/` run:

   ```bash
   vagrant up
   ```

6. Connect to the VM by running:

   ```bash
   vagrant ssh
   ```

8. Type `cd /vagrant/` to navigate to the shared repository.
    - "Files in the VM's /vagrant directory are shared with the vagrant folder on your computer. But other data inside the VM is not. For instance, the sqlalchemy database itself lives only inside the VM."

9. Download this repository in the `catalog/` folder

10. Set up the database:
    ```bash
    python catalogdb_setup.py
    ```

13. Insert dummy values:
    ```bash
    python fakedb.py
    ```

14. Run `application.py`:
    ```bash
    python application.py
    ```
15. Open `http://localhost:5000/` in your favourite Web browser, and enjoy.

## JSON Endpoints

Returns JSON of all categories
`/catalog.json`

Returns JSON of all category items
`/catalog/items/json`

Returns JSON of specific category items
`/catalog/<int:category_id>/<int:item_id>/json`

<VirtualHost *:80>
	ServerName 54.166.173.58
	ServerAdmin karojg@gmail.com
    WSGIDaemonProcess catalog python-path=/var/www/catalog:/var/www/catalog/venv/lib/python2.7/site-packages
    WSGIProcessGroup catalog
    WSGIScriptAlias / /var/www/catalog/catalog.wsgi
    <Directory /var/www/catalog/catalog/>
        Order allow,deny
        Allow from all
    </Directory>
    Alias /static /var/www/catalog/catalog/static
    <Directory /var/www/catalog/catalog/static/>
        Order allow,deny
        Allow from all
    </Directory>
    ErrorLog ${APACHE_LOG_DIR}/error.log
    LogLevel warn
    CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>