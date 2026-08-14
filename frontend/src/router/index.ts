import { createRouter, createWebHistory } from "vue-router"

import Home from "@/pages/Home.vue"
import Servicos from "@/pages/Servicos.vue"
import SPE from "@/pages/SPE.vue"
import Portal from "@/pages/PortalCliente.vue"
import Backoffice from "@/pages/Backoffice.vue"
import DashboardExecutivo from "@/pages/DashboardExecutivo.vue"
import LegalAssurance from "@/pages/LegalAssurance.vue"

export default createRouter({
history:createWebHistory(),
routes:[
{ path:"/", component:Home },
{ path:"/servicos", component:Servicos },
{ path:"/spe", component:SPE },
{ path:"/portal", component:Portal },
{ path:"/backoffice", component:Backoffice },
{ path:"/executivo", component:DashboardExecutivo }
,{ path:"/assurance", component:LegalAssurance }
]
})
