class HideForm{
    constructor(){
        this._HIDDEN = true;
    }

    getHidden(){
        return this._HIDDEN;
    }

    setHidden(truthy){
        this._HIDDEN = truthy;
    }
}