import { defineStore } from "pinia"

export const useJuridico = defineStore("juridico",{
state:()=>({
leads:[],
contratos:[],
spes:[]
}),
actions:{
addLead(l){
this.leads.push(l)
}
}
})
