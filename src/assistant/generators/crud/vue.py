import os
import re
from typing import Dict, List, Optional, Tuple

from jinja2 import Environment, FileSystemLoader, select_autoescape
from pgsql_parser import Column, ForeignKey, Table  # Added as requested, commented out


class CRUDVueGenerator:
    """
    Generates a basic Vue.js frontend for CRUD operations,
    including Dockerfile for the frontend.
    Supports one-to-many relationships for specified root tables.
    """

    def __init__(
        self,
        tables: List[Table],
        backend_api_url: str = "http://localhost:8000",
        root_table_names: Optional[List[str]] = None,
    ):
        """
        Args:
            tables: List of Table objects to generate Vue components for.
            backend_api_url: The base URL for the backend API.
            root_table_names: A list of table names that should be treated as "root"
                              tables, meaning their GET endpoints will eager-load
                              direct one-to-many relationships.
        """
        self.tables = tables
        self.backend_api_url = backend_api_url
        self.root_table_names = root_table_names if root_table_names is not None else []
        current_dir = os.path.dirname(os.path.abspath(__file__))
        template_dir = os.path.join(current_dir, "templates", "frontend")
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self._add_jinja_filters()

    def _add_jinja_filters(self):
        """Adds custom filters to the Jinja2 environment."""
        self.env.filters["snake_case"] = self._to_snake_case
        self.env.filters["pascal_case"] = self._to_pascal_case
        self.env.filters["singularize"] = self._singularize
        self.env.filters["pluralize"] = self._pluralize
        self.env.filters["sql_to_js_type"] = self._sql_type_to_js_type
        self.env.filters["get_pk_column"] = self._get_pk_column
        self.env.filters["get_pk_name"] = self._get_pk_name
        self.env.filters["get_default_value_for_type"] = (
            self._get_default_value_for_type
        )
        self.env.filters["get_child_tables"] = (
            self._get_child_tables
        )  # Add filter for child tables

    def _to_snake_case(self, name: str) -> str:
        """Converts PascalCase/CamelCase/Space-separated to snake_case."""
        name = name.replace(" ", "_")
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

    def _to_pascal_case(self, name: str) -> str:
        """Converts snake_case/kebab-case/space-separated to PascalCase."""
        return "".join(word.capitalize() for word in re.split(r"[-_ ]", name))

    def _singularize(self, name: str) -> str:
        """Basic singularization (for component names)."""
        if name.endswith("s") and not name.endswith("ss"):
            return name[:-1]
        return name

    def _pluralize(self, name: str) -> str:
        """Basic pluralization (for API paths)."""
        if not name.endswith("s"):
            return name + "s"
        return name

    def _sql_type_to_js_type(self, column: Column) -> str:
        """Converts SQL data types to JavaScript types (for initial values)."""
        data_type = column.data_type.lower()
        if data_type in ["varchar", "text", "char", "uuid", "json", "jsonb"]:
            return '""'
        elif data_type in ["integer", "smallint", "bigint", "serial", "bigserial"]:
            return "0"
        elif data_type in ["boolean"]:
            return "false"
        elif data_type in ["float", "double precision", "real", "numeric", "decimal"]:
            return "0.0"
        elif data_type in ["date", "timestamp", "timestamptz", "datetime"]:
            return "null"  # Or 'new Date().toISOString()' for current time
        elif data_type in ["bytea", "blob"]:
            return "null"
        return "null"  # Fallback for unhandled types

    def _get_pk_column(self, table: Table) -> Optional[Column]:
        """Returns the primary key column, assuming a single PK column for simplicity."""
        if table.primary_key and table.primary_key.columns:
            pk_col_name = table.primary_key.columns[0]
            return table.columns.get(pk_col_name)
        return None

    def _get_pk_name(self, table: Table) -> str:
        """Returns the name of the primary key column."""
        pk_column = self._get_pk_column(table)
        if pk_column:
            return pk_column.name
        return "id"  # Default to 'id'

    def _get_default_value_for_type(self, column: Column):
        """Returns a suitable default value for form initialization."""
        data_type = column.data_type.lower()
        if data_type in ["varchar", "text", "char", "uuid", "json", "jsonb"]:
            return '""'
        elif data_type in ["integer", "smallint", "bigint", "serial", "bigserial"]:
            return "0"
        elif data_type in ["boolean"]:
            return "false"
        elif data_type in ["float", "double precision", "real", "numeric", "decimal"]:
            return "0.0"
        elif data_type in ["date"]:
            return "null"  # Or a default date string if needed
        elif data_type in ["timestamp", "timestamptz", "datetime"]:
            return "null"  # Or a default datetime string if needed
        return "null"

    def _get_child_tables(self, parent_table: Table) -> List[Table]:
        """Returns a list of tables that have a foreign key referencing the parent_table."""
        children = []
        for table in self.tables:
            if table.name == parent_table.name:
                continue
            for fk in table.foreign_keys:
                if fk.ref_table == parent_table.name:
                    children.append(table)
                    break  # A table can only be a child once to a specific parent for simplicity
        return children

    def generate(self, output_dir: str = "frontend", force_overwrite: bool = False):
        """
        Generates complete Vue.js frontend structure.

        Args:
            output_dir: The base directory for the generated frontend files.
            force_overwrite: If True, overwrite existing files without prompt.
                             If False, skip existing files.
        """
        base_path = os.path.join(os.getcwd(), output_dir)
        os.makedirs(base_path, exist_ok=True)
        os.makedirs(os.path.join(base_path, "public"), exist_ok=True)
        os.makedirs(os.path.join(base_path, "src"), exist_ok=True)
        os.makedirs(os.path.join(base_path, "src", "assets"), exist_ok=True)
        os.makedirs(os.path.join(base_path, "src", "components"), exist_ok=True)
        os.makedirs(os.path.join(base_path, "src", "views"), exist_ok=True)
        os.makedirs(os.path.join(base_path, "src", "router"), exist_ok=True)

        # Helper to write files with overwrite control
        def write_file(path, content):
            if os.path.exists(path) and not force_overwrite:
                print(f"Skipping existing file: {path}")
                return
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                f.write(content)
            print(f"Generated: {path}")

        all_table_names_snake = [self._to_snake_case(t.name) for t in self.tables]
        all_table_names_pascal = [self._to_pascal_case(t.name) for t in self.tables]

        # Generate per-table components and views
        for table in self.tables:
            table_snake_case = self._to_snake_case(table.name)
            table_pascal_case = self._to_pascal_case(table.name)
            table_singular_pascal = self._to_pascal_case(self._singularize(table.name))
            table_plural_pascal = self._to_pascal_case(self._pluralize(table.name))
            table_plural_snake = self._to_snake_case(self._pluralize(table.name))

            context = {
                "table": table,
                "table_snake_case": table_snake_case,
                "table_pascal_case": table_pascal_case,
                "table_singular_pascal": table_singular_pascal,
                "table_plural_pascal": table_plural_pascal,
                "table_plural_snake": table_plural_snake,
                "columns": list(table.columns.values()),
                "pk_column": self._get_pk_column(table),
                "pk_name": self._get_pk_name(table),
                "backend_api_url": self.backend_api_url,
                "is_root_table": table.name in self.root_table_names,
                "all_tables": self.tables,  # Pass all tables to frontend templates for relationship info
                "child_tables": self._get_child_tables(
                    table
                ),  # Get direct children for this table
            }

            # Generate Component
            component_template = self.env.get_template("Component.vue.j2")
            component_content = component_template.render(context)
            write_file(
                os.path.join(
                    base_path, "src", "components", f"{table_singular_pascal}.vue"
                ),
                component_content,
            )

            # Generate View
            view_template = self.env.get_template("View.vue.j2")
            view_content = view_template.render(context)
            write_file(
                os.path.join(
                    base_path, "src", "views", f"{table_plural_pascal}View.vue"
                ),
                view_content,
            )

        # Generate common files
        common_context = {
            "tables": self.tables,
            "all_table_names_snake": all_table_names_snake,
            "all_table_names_pascal": all_table_names_pascal,
            "backend_api_url": self.backend_api_url,
        }

        # index.html
        index_html_template = self.env.get_template("index.html.j2")
        write_file(
            os.path.join(base_path, "public", "index.html"),
            index_html_template.render(common_context),
        )

        # App.vue
        app_vue_template = self.env.get_template("App.vue.j2")
        write_file(
            os.path.join(base_path, "src", "App.vue"),
            app_vue_template.render(common_context),
        )

        # main.js
        main_js_template = self.env.get_template("main.js.j2")
        write_file(
            os.path.join(base_path, "src", "main.js"),
            main_js_template.render(common_context),
        )

        # router/index.js
        router_index_js_template = self.env.get_template("router_index.js.j2")
        write_file(
            os.path.join(base_path, "src", "router", "index.js"),
            router_index_js_template.render(common_context),
        )

        # .env.development
        env_dev_template = self.env.get_template(".env.development.j2")
        write_file(
            os.path.join(base_path, ".env.development"),
            env_dev_template.render(common_context),
        )

        # .env.production
        env_prod_template = self.env.get_template(".env.production.j2")
        write_file(
            os.path.join(base_path, ".env.production"),
            env_prod_template.render(common_context),
        )

        # package.json
        package_json_template = self.env.get_template("package.json.j2")
        write_file(
            os.path.join(base_path, "package.json"),
            package_json_template.render(common_context),
        )

        # vite.config.js
        vite_config_template = self.env.get_template("vite.config.js.j2")
        write_file(
            os.path.join(base_path, "vite.config.js"),
            vite_config_template.render(common_context),
        )

        # Dockerfile
        dockerfile_template = self.env.get_template("Dockerfile.j2")
        write_file(
            os.path.join(base_path, "Dockerfile"),
            dockerfile_template.render(common_context),
        )

        print(f"Vue.js frontend generated successfully in '{output_dir}' directory.")


# --- Placeholder Jinja2 Templates (These would typically be in templates/frontend/) ---

# Component.vue.j2
COMPONENT_VUE_TEMPLATE = """
<template>
  <div class="{{ table_snake_case }}-item">
    <h3>{{ table_singular_pascal }} Details</h3>
    <form @submit.prevent="save{{ table_singular_pascal }}">
      {% for column in columns %}
      {% if not column.is_primary %}
      <div class="p-field">
        <label for="{{ column.name | snake_case }}">{{ column.name | pascal_case }}:</label>
        {% if column.data_type == 'boolean' %}
        <Checkbox v-model="editable{{ table_singular_pascal }}.{{ column.name | snake_case }}" :binary="true" />
        {% else %}
        <InputText id="{{ column.name | snake_case }}" v-model="editable{{ table_singular_pascal }}.{{ column.name | snake_case }}" {% if not column.nullable %}required{% endif %} />
        {% endif %}
      </div>
      {% endif %}
      {% endfor %}
      <Button type="submit" :label="editable{{ table_singular_pascal }}.{{ pk_name | snake_case }} ? 'Update' : 'Create'" icon="pi pi-save" class="p-button-success" />
      <Button type="button" label="Cancel" icon="pi pi-times" class="p-button-secondary" @click="cancelEdit" />
    </form>
  </div>
</template>

<script>
import axios from 'axios';
// PrimeVue components are globally registered in main.js, no need to import here
// import InputText from 'primevue/inputtext';
// import Button from 'primevue/button';
// import Checkbox from 'primevue/checkbox';

export default {
  name: '{{ table_singular_pascal }}Component',
  props: {
    {{ table_snake_case }}: {
      type: Object,
      default: () => ({
        {% for column in columns %}
        {% if not column.is_primary %}
        {{ column.name | snake_case }}: {{ column | get_default_value_for_type }},
        {% endif %}
        {% endfor %}
      })
    }
  },
  data() {
    return {
      editable{{ table_singular_pascal }}: { ...this.{{ table_snake_case }} },
      backendUrl: import.meta.env.VITE_APP_BACKEND_API_URL || '{{ backend_api_url }}'
    };
  },
  watch: {
    {{ table_snake_case }}: {
      handler(newVal) {
        this.editable{{ table_singular_pascal }} = { ...newVal };
      },
      deep: true,
      immediate: true
    }
  },
  methods: {
    async save{{ table_singular_pascal }}() {
      try {
        let response;
        if (this.editable{{ table_singular_pascal }}.{{ pk_name | snake_case }}) {
          // Update existing
          const response = await axios.put(
            `${this.backendUrl}/{{ table_plural_snake }}/${this.editable{{ table_singular_pascal }}.{{ pk_name | snake_case }}}`,
            this.editable{{ table_singular_pascal }}
          );
          this.$toast.add({severity:'success', summary: 'Success', detail:'{{ table_singular_pascal }} Updated', life: 3000});
          this.$emit('{{ table_snake_case }}Updated', response.data);
        } else {
          // Create new
          const response = await axios.post(
            `${this.backendUrl}/{{ table_plural_snake }}`,
            this.editable{{ table_singular_pascal }}
          );
          this.$toast.add({severity:'success', summary: 'Success', detail:'{{ table_singular_pascal }} Created', life: 3000});
          this.$emit('{{ table_snake_case }}Created', response.data);
        }
        this.resetForm();
      } catch (error) {
        console.error("Error saving {{ table_snake_case }}:", error);
        this.$toast.add({severity:'error', summary: 'Error', detail:'Failed to save {{ table_snake_case }}. Check console.', life: 3000});
      }
    },
    resetForm() {
      this.editable{{ table_singular_pascal }} = {
        {% for column in columns %}
        {% if not column.is_primary %}
        {{ column.name | snake_case }}: {{ column | get_default_value_for_type }},
        {% endif %}
        {% endfor %}
      };
    },
    cancelEdit() {
      this.$emit('cancelEdit');
    }
  }
};
</script>

<style scoped>
/* PrimeVue will handle most styling, but custom adjustments can go here */
.{{ table_snake_case }}-item {
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
  background-color: var(--surface-card); /* Using PrimeVue CSS variables */
}

.p-field {
  margin-bottom: 1rem;
}

.p-field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
}

.p-button {
  margin-right: 0.5rem;
}
</style>
"""

# View.vue.j2
VIEW_VUE_TEMPLATE = """
<template>
  <div class="{{ table_snake_case }}-view">
    <Toast />
    <ConfirmDialog></ConfirmDialog>
    <h1>Manage {{ table_plural_pascal }}</h1>

    <Button label="Add New {{ table_singular_pascal }}" icon="pi pi-plus" @click="startCreate" class="p-button-primary" />

    <Dialog v-model:visible="displayDialog" :header="editing{{ table_singular_pascal }} && editing{{ table_singular_pascal }}.{{ pk_name | snake_case }} ? 'Edit {{ table_singular_pascal }}' : 'Create {{ table_singular_pascal }}'" :modal="true" :style="{width: '50vw'}">
      <{{ table_singular_pascal }}Component
        :{{ table_snake_case }}="editing{{ table_singular_pascal }}"
        @{{ table_snake_case }}Created="handle{{ table_singular_pascal }}Created"
        @{{ table_snake_case }}Updated="handle{{ table_singular_pascal }}Updated"
        @cancelEdit="cancelEdit"
      />
    </Dialog>

    <h2>{{ table_plural_pascal }} List</h2>
    <DataTable :value="{{ '{{' }} {{ table_plural_snake }} {{ '}}' }}" responsiveLayout="scroll">
      <Column field="{{ pk_name | snake_case }}" header="ID"></Column>
      {% for column in columns %}
      {% if not column.is_primary %}
      <Column field="{{ column.name | snake_case }}" header="{{ column.name | pascal_case }}"></Column>
      {% endif %}
      {% endfor %}

      {% if is_root_table %}
      {% for child_table in child_tables %}
      <Column header="{{ child_table.name | pluralize | pascal_case }}">
        <template #body="slotProps">
          <ul v-if="slotProps.data.{{ child_table.name | pluralize | snake_case }}_collection && slotProps.data.{{ child_table.name | pluralize | snake_case }}_collection.length">
            <li v-for="child in slotProps.data.{{ child_table.name | pluralize | snake_case }}_collection" :key="child.{{ child_table | get_pk_name | snake_case }}">
              {{ child_table.name | singularize | pascal_case }} ID: {{ '{{' }} child.{{ child_table | get_pk_name | snake_case }} {{ '}}' }}
              {% for child_column in child_table.columns.values() %}
              {% if not child_column.is_primary %}
              , {{ child_column.name | snake_case }}: {{ '{{' }} child.{{ child_column.name | snake_case }} {{ '}}' }}
              {% endif %}
              {% endfor %}
            </li>
          </ul>
          <span v-else>No {{ child_table.name | pluralize | pascal_case }}</span>
        </template>
      </Column>
      {% endfor %}
      {% endif %}

      <Column header="Actions">
        <template #body="slotProps">
          <Button icon="pi pi-pencil" class="p-button-rounded p-button-success p-mr-2" @click="startEdit(slotProps.data)" />
          <Button icon="pi pi-trash" class="p-button-rounded p-button-danger" @click="confirmDelete(slotProps.data.{{ pk_name | snake_case }})" />
        </template>
      </Column>
    </DataTable>
  </div>
</template>

<script>
import axios from 'axios';
import {{ table_singular_pascal }}Component from '@/components/{{ table_singular_pascal }}.vue';
// PrimeVue components imported globally in main.js

export default {
  name: '{{ table_plural_pascal }}View',
  components: {
    {{ table_singular_pascal }}Component,
  },
  data() {
    return {
      {{ table_plural_snake }}: [],
      editing{{ table_singular_pascal }}: null,
      displayDialog: false,
      backendUrl: import.meta.env.VITE_APP_BACKEND_API_URL || '{{ backend_api_url }}'
    };
  },
  created() {
    this.fetch{{ table_plural_pascal }}();
  },
  methods: {
    async fetch{{ table_plural_pascal }}() {
      try {
        let url = `${this.backendUrl}/{{ table_plural_snake }}`;
        // If this is a root table, request eager loading of relationships
        if (this.isRootTable) {
          url += '?eager_load_relations=true';
        }
        const response = await axios.get(url);
        this.{{ table_plural_snake }} = response.data;
      } catch (error) {
        console.error("Error fetching {{ table_plural_snake }}:", error);
        this.$toast.add({severity:'error', summary: 'Error', detail:'Failed to fetch {{ table_plural_snake }}. Check console.', life: 3000});
      }
    },
    startCreate() {
      this.editing{{ table_singular_pascal }} = {
        {% for column in columns %}
        {% if not column.is_primary %}
        {{ column.name | snake_case }}: {{ column | get_default_value_for_type }},
        {% endif %}
        {% endfor %}
      };
      this.displayDialog = true;
    },
    startEdit({{ table_snake_case }}ToEdit) {
      this.editing{{ table_singular_pascal }} = { ...{{ table_snake_case }}ToEdit };
      this.displayDialog = true;
    },
    cancelEdit() {
      this.editing{{ table_singular_pascal }} = null;
      this.displayDialog = false;
    },
    handle{{ table_singular_pascal }}Created(new{{ table_singular_pascal }}) {
      // Refresh the list to ensure relationships are correctly fetched if needed
      this.displayDialog = false;
      this.fetch{{ table_plural_pascal }}();
      this.$toast.add({severity:'success', summary: 'Success', detail:'{{ table_singular_pascal }} Created', life: 3000});
    },
    handle{{ table_singular_pascal }}Updated(updated{{ table_singular_pascal }}) {
      // Refresh the list to ensure relationships are correctly fetched if needed
      this.displayDialog = false;
      this.fetch{{ table_plural_pascal }}();
      this.$toast.add({severity:'success', summary: 'Success', detail:'{{ table_singular_pascal }} Updated', life: 3000});
    },
    confirmDelete({{ pk_name | snake_case }}) {
      this.$confirm.require({
        message: 'Are you sure you want to delete this item?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        accept: () => {
          this.delete{{ table_singular_pascal }}({{ pk_name | snake_case }});
        },
        reject: () => {
          this.$toast.add({severity:'info', summary:'Cancelled', detail:'Delete operation cancelled', life: 3000});
        }
      });
    },
    async delete{{ table_singular_pascal }}(idToDelete) { // Renamed parameter to avoid conflict
      try {
        await axios.delete(`${this.backendUrl}/{{ table_plural_snake }}/` + idToDelete);
        this.{{ table_plural_snake }} = this.{{ table_plural_snake }}.filter(item => item.{{ pk_name | snake_case }} !== idToDelete);
        this.$toast.add({severity:'success', summary: 'Success', detail:'{{ table_singular_pascal }} Deleted', life: 3000});
      } catch (error) {
        console.error("Error deleting {{ table_snake_case }}:", error);
        this.$toast.add({severity:'error', summary: 'Error', detail:'Failed to delete {{ table_snake_case }}. Check console.', life: 3000});
      }
    }
  },
  computed: {
    isRootTable() {
      // Determine if the current view's table is specified as a root table
      // This is a simplified check. For more robust solution, pass this from generator.
      const currentPath = this.$route.path;
      const currentTableSlug = currentPath.split('/').pop(); // e.g., 'users' from '/users'
      // Compare with the plural snake case of the table name
      return currentTableSlug === '{{ table_plural_snake }}' && {{ 'true' if table.name in root_table_names else 'false' }};
    }
  }
};
</script>

<style scoped>
.{{ table_snake_case }}-view {
  max-width: 1200px; /* Wider for DataTable */
  margin: 20px auto;
  padding: 20px;
  background-color: var(--surface-card);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

h1, h2 {
  color: var(--text-color);
  text-align: center;
  margin-bottom: 20px;
}

.p-button {
  margin-bottom: 20px;
}

/* Styles for DataTable and its elements can be further customized */
.p-datatable .p-datatable-tbody > tr > td {
  text-align: left;
}

.actions .p-button {
  margin-left: 0.5rem;
}
</style>
"""

# index.html.j2
INDEX_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" href="/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Vue CRUD App</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.js"></script>
  </body>
</html>
"""

# App.vue.j2
APP_VUE_TEMPLATE = """
<template>
  <nav>
    <router-link to="/">Home</router-link> |
    {% for table in tables %}
    <router-link to="/{{ table.name | pluralize | snake_case }}">{{ table.name | pluralize | pascal_case }}</router-link>{% if not loop.last %} | {% endif %}
    {% endfor %}
  </nav>
  <router-view/>
</template>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

nav {
  padding: 30px;
}

nav a {
  font-weight: bold;
  color: #2c3e50;
}

nav a.router-link-exact-active {
  color: #42b983;
}
</style>
"""

# main.js.j2
MAIN_JS_TEMPLATE = """
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import PrimeVue from 'primevue/config';
import ConfirmationService from 'primevue/confirmationservice';
import ToastService from 'primevue/toastservice';

// PrimeVue Themes and Core CSS
import 'primevue/resources/themes/saga-blue/theme.css'; // Or another theme, e.g., saga-blue, saga-green, saga-orange, saga-purple
import 'primevue/resources/primevue.min.css'; // Core CSS
import 'primeicons/primeicons.css'; // PrimeIcons

// PrimeVue Components to register globally (for easy use without explicit import in every component)
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Checkbox from 'primevue/checkbox';
import Dialog from 'primevue/dialog';
import Toast from 'primevue/toast';
import ConfirmDialog from 'primevue/confirmdialog';


const app = createApp(App);
app.use(router);
app.use(PrimeVue, { ripple: true }); // Enable ripple effect
app.use(ConfirmationService); // For confirm dialogs
app.use(ToastService); // For toast notifications

// Register global components
app.component('InputText', InputText);
app.component('Button', Button);
app.component('DataTable', DataTable);
app.component('Column', Column);
app.component('Checkbox', Checkbox);
app.component('Dialog', Dialog);
app.component('Toast', Toast);
app.component('ConfirmDialog', ConfirmDialog);


app.mount('#app');
"""

# router_index.js.j2
ROUTER_INDEX_JS_TEMPLATE = """
import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
{% for table in tables %}
import {{ table.name | pluralize | pascal_case }}View from '../views/{{ table.name | pluralize | pascal_case }}View.vue'
{% endfor %}

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {% for table in tables %}
  {
    path: '/{{ table.name | pluralize | snake_case }}',
    name: '{{ table.name | pluralize | snake_case }}',
    component: {{ table.name | pluralize | pascal_case }}View
  },
  {% endfor %}
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router
"""

# .env.development.j2
ENV_DEVELOPMENT_TEMPLATE = """
VITE_APP_BACKEND_API_URL={{ backend_api_url }}
"""

# .env.production.j2
ENV_PRODUCTION_TEMPLATE = """
VITE_APP_BACKEND_API_URL=http://localhost:8000 # Replace with your production backend URL
"""

# package.json.j2
PACKAGE_JSON_TEMPLATE = """
{
  "name": "vue-crud-app",
  "version": "0.0.0",
  "private": true,
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "axios": "^1.7.2",
    "vue": "^3.4.29",
    "vue-router": "^4.3.3",
    "primevue": "^3.52.0",
    "primeicons": "^7.0.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.5",
    "vite": "^5.3.1"
  }
}
"""

# vite.config.js.j2
VITE_CONFIG_TEMPLATE = """
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path' // Import path module

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'), // Configure the @ alias to point to the src directory
    },
  },
  server: {
    host: true, // This makes the server accessible externally
    port: 6162, // Set the desired port
  },
})
"""

# Dockerfile.j2 for Vue Frontend
DOCKERFILE_VUE_TEMPLATE = """
# Use a Node.js base image for building the Vue app
FROM node:18-alpine as build-stage

WORKDIR /app

# Copy package.json and install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the Vue application for production
RUN npm run build

# Use a lightweight web server (Nginx) for serving the static files
FROM nginx:stable-alpine as production-stage

# Copy the built Vue app from the build stage
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Copy custom Nginx configuration (optional, but good for SPAs)
# If you have a custom nginx.conf, uncomment and copy it:
# COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
"""


def create_vue_template_files(template_dir="templates/frontend"):
    """Helper to create dummy Vue template files for demonstration."""
    os.makedirs(template_dir, exist_ok=True)
    with open(os.path.join(template_dir, "Component.vue.j2"), "w") as f:
        f.write(COMPONENT_VUE_TEMPLATE.strip())
    with open(os.path.join(template_dir, "View.vue.j2"), "w") as f:
        f.write(VIEW_VUE_TEMPLATE.strip())
    with open(os.path.join(template_dir, "index.html.j2"), "w") as f:
        f.write(INDEX_HTML_TEMPLATE.strip())
    with open(os.path.join(template_dir, "App.vue.j2"), "w") as f:
        f.write(APP_VUE_TEMPLATE.strip())
    with open(os.path.join(template_dir, "main.js.j2"), "w") as f:
        f.write(MAIN_JS_TEMPLATE.strip())
    with open(os.path.join(template_dir, "router_index.js.j2"), "w") as f:
        f.write(ROUTER_INDEX_JS_TEMPLATE.strip())
    with open(os.path.join(template_dir, ".env.development.j2"), "w") as f:
        f.write(ENV_DEVELOPMENT_TEMPLATE.strip())
    with open(os.path.join(template_dir, ".env.production.j2"), "w") as f:
        f.write(ENV_PRODUCTION_TEMPLATE.strip())
    with open(os.path.join(template_dir, "package.json.j2"), "w") as f:
        f.write(PACKAGE_JSON_TEMPLATE.strip())
    with open(
        os.path.join(template_dir, "vite.config.js.j2"), "w"
    ) as f:  # New vite.config.js template
        f.write(VITE_CONFIG_TEMPLATE.strip())
    with open(os.path.join(template_dir, "Dockerfile.j2"), "w") as f:
        f.write(DOCKERFILE_VUE_TEMPLATE.strip())
    print(f"Jinja2 Vue template files created in '{template_dir}'")


def main_vue_generator(
    tables_to_generate: List[Table],
    backend_api_url: str,
    root_table_names: List[str],
    force_overwrite: bool = False,
):
    create_vue_template_files()
    generator = CRUDVueGenerator(
        tables=tables_to_generate,
        backend_api_url=backend_api_url,
        root_table_names=root_table_names,
    )
    generator.generate(output_dir="frontend", force_overwrite=force_overwrite)
