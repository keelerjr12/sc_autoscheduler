import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class ConfigService {
  private SCHEME = 'http://';
  private HOST = 'localhost';
  private PORT = 8000;
  private SUB_DIRECTORY = 'api'

  getApiUrl(): string {
    return this.SCHEME + this.HOST + ':' + this.PORT + '/' + this.SUB_DIRECTORY + '/';
  }
}
