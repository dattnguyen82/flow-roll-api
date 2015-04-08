package org.flow;

import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.RequestMapping;

@RestController
public class MainController {
    
    @RequestMapping("/")
    public String index() {
        return "BJJ Asset Operations";
    }

    
}
