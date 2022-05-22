 

# Virtual Museum Interactive Machine Learning

## 

### Repository Structure

```bash
/
├── virtual_museum_manager
│   ├── ...
├── virtual_museum_visualization
├── docker-compose.yml
```

- **virtual_museum_manager directory**: contains the logic that is in charge of managing the simulation (based on the MESA framework).
- **virtual_museum_visualization directory**: web server users interact with. The main purpose of this module is to offer an enhanced visualization component that completely replaces MESA's bulilt-in visualization canvas. The visualization component is based on the RAMEN framework which offers a 3D environment to carry out MESA simulations, dramatically improving  MESA's  standard 2D canvas view. It has been adapted to offer a first-person simulation of a museum tour.

### Running the Scenario

Since the project has been dockerized, running it is as simple as launching the docker-compose file in the root directory and opening a web browser to start the virtual museum tour! In other words, do the following:

1. ```bash
   sudo docker-compose up --build
   ```

2. Once the docker containers are up and running, open your favourite browser and go to the following address: http://localhost:1234/

3. If it is the first time, you will need to register in order to access the virtual museum tour. Once registered, log in and enjoy the visit!